from numba import jit
import os
import pickle
import shutil
from math import floor, ceil
import array
import numpy
import itertools
from PIL import Image, ImageDraw, ImageFilter
from collections import defaultdict
import struct
import hashlib
import O4_File_Names as FNAMES
import O4_Geo_Utils as GEO
import O4_Mask_Utils as MASK
import O4_Mesh_Utils as MESH
import O4_UI_Utils as UI
import O4_DEM_Utils as DEM

#min_cliff=0.8
min_cliff=0
min_cliff2=min_cliff**2
build_normal_maps = False

def build_texture_normal_map(tile,texture_attributes):
    til_x_left, til_y_top, zoomlevel, provider_code = texture_attributes
    (latmax,lonmin) = GEO.gtile_to_wgs84(til_x_left, til_y_top, zoomlevel)
    (latmin,lonmax) = GEO.gtile_to_wgs84(til_x_left + 16, til_y_top + 16, zoomlevel)
    pixxmin = round((lonmin - (tile.dem.lon + tile.dem.x0))/(tile.dem.x1-tile.dem.x0)*tile.dem.nxdem)
    pixxmax = round((lonmax - (tile.dem.lon + tile.dem.x0))/(tile.dem.x1-tile.dem.x0)*tile.dem.nxdem)
    pixymin = round((tile.dem.lat + tile.dem.y1 - latmax)/(tile.dem.y1-tile.dem.y0)*tile.dem.nydem)
    pixymax = round((tile.dem.lat + tile.dem.y1 - latmin)/(tile.dem.y1-tile.dem.y0)*tile.dem.nydem)
    target_dir = os.path.join(tile.build_dir,"textures")
    tile.dem.normal_map.crop((pixxmin,pixymin,pixxmax,pixymax)).resize((1024,1024),Image.BICUBIC).filter(ImageFilter.GaussianBlur(1)).save(os.path.join(target_dir,FNAMES.normal_map_file(til_x_left,til_y_top,zoomlevel)))
    
    
experimental_water_zl=14
experimental_water_provider_code='SEA'

# For Laminar test suite, beware not to use imprint_masks if set to True as this doesn't makes sense!
use_test_texture=False  

@jit(nopython=True)
def barycenter(n1,n2,n3,node_coords):
    return ((node_coords[5*n1]+node_coords[5*n2]+node_coords[5*n3])/3,(node_coords[5*n1+1]+node_coords[5*n2+1]+node_coords[5*n3+1])/3)
    



##############################################################################
def zone_list_to_ortho_dico(tile):
        # tile.zone_list is a list of 3-uples of the form ([(lat0,lat0),...(latN,lonN),zoomlevel,provider_code)
        # where higher lines have priority over lower ones.
        masks_im=Image.new("L",(4096,4096),'black')
        masks_draw=ImageDraw.Draw(masks_im)
        airport_array=numpy.zeros((4096,4096),dtype=numpy.bool)
        if tile.cover_airports_with_highres in ['True','ICAO']:
            UI.vprint(1,"-> Checking airport locations for upgraded zoomlevel.")
            try:
                f=open(FNAMES.apt_file(tile),'rb')
                dico_airports=pickle.load(f)
                f.close()
            except:
                UI.vprint(1,"   WARNING: File",FNAMES.apt_file(tile),"is missing (erased after Step 1?), cannot check airport info for upgraded zoomlevel.")
                dico_airports={}
            if tile.cover_airports_with_highres=='ICAO':
                airports_list=[airport for airport in dico_airports if dico_airports[airport]['key_type']=='icao']
            else:
                airports_list=dico_airports.keys()
            for airport in airports_list:
                (xmin,ymin,xmax,ymax)=dico_airports[airport]['boundary'].bounds
                # extension
                xmin-=1000*tile.cover_extent*GEO.m_to_lon(tile.lat)
                xmax+=1000*tile.cover_extent*GEO.m_to_lon(tile.lat)
                ymax+=1000*tile.cover_extent*GEO.m_to_lat
                ymin-=1000*tile.cover_extent*GEO.m_to_lat
                # round off to texture boundaries at tile.cover_zl zoomlevel
                (til_x_left,til_y_top)=GEO.wgs84_to_orthogrid(ymax+tile.lat,xmin+tile.lon,tile.cover_zl)
                (ymax,xmin)=GEO.gtile_to_wgs84(til_x_left,til_y_top,tile.cover_zl)
                ymax-=tile.lat; xmin-=tile.lon
                (til_x_left2,til_y_top2)=GEO.wgs84_to_orthogrid(ymin+tile.lat,xmax+tile.lon,tile.cover_zl)
                (ymin,xmax)=GEO.gtile_to_wgs84(til_x_left2+16,til_y_top2+16,tile.cover_zl)
                ymin-=tile.lat; xmax-=tile.lon
                xmin=max(0,xmin); xmax=min(1,xmax); ymin=max(0,ymin); ymax=min(1,ymax)
                # mark to airport_array
                colmin=round(xmin*4095)
                colmax=round(xmax*4095)
                rowmax=round((1-ymin)*4095)
                rowmin=round((1-ymax)*4095)
                airport_array[rowmin:rowmax+1,colmin:colmax+1]=1
        dico_customzl={}        
        dico_tmp={}
        til_x_min,til_y_min=GEO.wgs84_to_orthogrid(tile.lat+1,tile.lon,tile.mesh_zl)
        til_x_max,til_y_max=GEO.wgs84_to_orthogrid(tile.lat,tile.lon+1,tile.mesh_zl) 
        i=1
        base_zone=((tile.lat,tile.lon,tile.lat,tile.lon+1,tile.lat+1,tile.lon+1,tile.lat+1,tile.lon,tile.lat,tile.lon),tile.default_zl,tile.default_website)
        for region in [base_zone]+tile.zone_list[::-1]:
            dico_tmp[i]=(region[1],region[2])
            pol=[(round((x-tile.lon)*4095),round((tile.lat+1-y)*4095)) for (x,y) in zip(region[0][1::2],region[0][::2])]
            masks_draw.polygon(pol,fill=i)
            i+=1
        for til_x in range(til_x_min,til_x_max+1,16):
            for til_y in range(til_y_min,til_y_max+1,16):
                (latp,lonp)=GEO.gtile_to_wgs84(til_x+8,til_y+8,tile.mesh_zl)
                lonp=max(min(lonp,tile.lon+1),tile.lon) 
                latp=max(min(latp,tile.lat+1),tile.lat) 
                x=round((lonp-tile.lon)*4095)
                y=round((tile.lat+1-latp)*4095)
                (zoomlevel,provider_code)=dico_tmp[masks_im.getpixel((x,y))]
                if airport_array[y,x]: 
                    zoomlevel=max(zoomlevel,tile.cover_zl)
                til_x_text=16*(int(til_x/2**(tile.mesh_zl-zoomlevel))//16)
                til_y_text=16*(int(til_y/2**(tile.mesh_zl-zoomlevel))//16)
                dico_customzl[(til_x,til_y)]=(til_x_text,til_y_text,zoomlevel,provider_code)
        if tile.cover_airports_with_highres=='Existing':
            # what we find in the texture folder of the existing tile
            for f in os.listdir(os.path.join(tile.build_dir,'textures')):
                if f[-4:]!='.dds': continue
                items=f.split('_')
                (til_y_text,til_x_text)=[int(x) for x in items[:2]]
                zoomlevel=int(items[-1][-6:-4])
                provider_code='_'.join(items[2:])[:-6]
                for til_x in range(til_x_text*2**(tile.mesh_zl-zoomlevel),(til_x_text+16)*2**(tile.mesh_zl-zoomlevel)):
                    for til_y in range(til_y_text*2**(tile.mesh_zl-zoomlevel),(til_y_text+16)*2**(tile.mesh_zl-zoomlevel)):
                        if ((til_x,til_y) not in dico_customzl) or dico_customzl[(til_x,til_y)][2]<=zoomlevel:
                            dico_customzl[(til_x,til_y)]=(til_x_text,til_y_text,zoomlevel,provider_code)
        return dico_customzl
##############################################################################

##############################################################################
def create_terrain_file(tile,texture_file_name,til_x_left,til_y_top,zoomlevel,provider_code,tri_type,is_overlay):
    if not os.path.exists(os.path.join(tile.build_dir,'terrain')):
        os.makedirs(os.path.join(tile.build_dir,'terrain'))
    suffix='_water' if tri_type==1 else '_sea' if tri_type==2 else ''
    if is_overlay: suffix+='_overlay'
    ter_file_name=texture_file_name[:-4]+suffix+'.ter'
    if use_test_texture: texture_file_name='test_texture.dds'
    with open(os.path.join(tile.build_dir,'terrain',ter_file_name),'w') as f:
        f.write('A\n800\nTERRAIN\n\n')
        [lat_med,lon_med]=GEO.gtile_to_wgs84(til_x_left+8,til_y_top+8,zoomlevel)
        texture_approx_size=int(GEO.webmercator_pixel_size(lat_med,zoomlevel)*4096)
        f.write('LOAD_CENTER '+'{:.5f}'.format(lat_med)+' '\
               +'{:.5f}'.format(lon_med)+' '\
               +str(texture_approx_size)+' 4096\n')
        f.write('BASE_TEX_NOWRAP ../textures/'+texture_file_name+'\n')
        if tri_type in (1,2) and not is_overlay: # experimental water
            f.write('TEXTURE_NORMAL '+str(2**(17-zoomlevel))+' ../textures/water_normal_map.dds\n')
            f.write('GLOBAL_specular 1.0\n')
            f.write('NORMAL_METALNESS\n')
            if not os.path.exists(os.path.join(tile.build_dir,'textures','water_normal_map.dds')):
                shutil.copy(os.path.join(FNAMES.Utils_dir,'water_normal_map.dds'),os.path.join(tile.build_dir,'textures'))
        elif tri_type==1 or (tri_type==2 and is_overlay=='ratio_water'): #constant transparency level       
            f.write('BORDER_TEX ../textures/water_transition.png\n')
            if not os.path.exists(os.path.join(tile.build_dir,'textures','water_transition.png')):
                shutil.copy(os.path.join(FNAMES.Utils_dir,'water_transition.png'),os.path.join(tile.build_dir,'textures'))
        elif tri_type==2 and not tile.imprint_masks_to_dds: #border_tex mask
            f.write('LOAD_CENTER_BORDER '+'{:.5f}'.format(lat_med)+' '\
               +'{:.5f}'.format(lon_med)+' '+str(texture_approx_size)+' '+str(4096//2**(zoomlevel-tile.mask_zl))+'\n')
            f.write('BORDER_TEX ../textures/'+FNAMES.mask_file(til_x_left,til_y_top,zoomlevel,provider_code)+'\n')
        elif tri_type==2 and tile.imprint_masks_to_dds: #dxt5 with normal map
            if (tile.experimental_water & 2):
                f.write('TEXTURE_NORMAL '+str(2**(17-zoomlevel))+' ../textures/water_normal_map.dds\n')
                f.write('GLOBAL_specular 1.0\n')
                f.write('NORMAL_METALNESS\n')
                if not os.path.exists(os.path.join(tile.build_dir,'textures','water_normal_map.dds')):
                    shutil.copy(os.path.join(FNAMES.Utils_dir,'water_normal_map.dds'),os.path.join(tile.build_dir,'textures'))
            elif build_normal_maps:
                f.write('TEXTURE_NORMAL 1  ../textures/'+FNAMES.normal_map_file(til_x_left,til_y_top,zoomlevel)+'\n')
                f.write('GLOBAL_specular 1.0\n')
                f.write('NORMAL_METALNESS\n')
        if not tri_type and build_normal_maps:
            f.write('TEXTURE_NORMAL 1  ../textures/'+FNAMES.normal_map_file(til_x_left,til_y_top,zoomlevel)+'\n')
            f.write('GLOBAL_specular 1.0\n')
            f.write('NORMAL_METALNESS\n')
        if not tri_type and tile.use_decal_on_terrain:
            f.write('DECAL_LIB lib/g10/decals/maquify_2_green_key.dcl\n')
        if tri_type in (1,2):
            f.write('WET\n')
        else:
            f.write('NO_ALPHA\n')
        if tri_type in (1,2) or not tile.terrain_casts_shadows:
            f.write('NO_SHADOW\n')
        return ter_file_name


##############################################################################
@jit(nopython=True)
def poolification(nbr_nodes, node_coords, lat, lon, divx, divy, normal_map_strength):
    invdivx=1/divx
    invdivy=1/divy
    ldivx=divx*65535
    ldivy=divy*65535
    boxx=divx+1
    boxy=divy+1
    node_icoords=numpy.zeros(5*nbr_nodes, dtype=numpy.uint16)
    node_poolx=((node_coords[::5]-lon)*divx).astype(numpy.uint16)
    node_icoords[0::5]=(node_coords[::5]-lon-node_poolx*invdivx)*ldivx
    node_pooly=((node_coords[1::5]-lat)*divy).astype(numpy.uint16)
    node_icoords[1::5]=(node_coords[1::5]-lat-node_pooly*invdivy)*ldivy
    max_alt=-499*numpy.ones(boxx*boxy, dtype=numpy.float64)
    min_alt=8999*numpy.ones(boxx*boxy, dtype=numpy.float64)
    scal_alt=numpy.zeros(boxx*boxy, dtype=numpy.uint16)
    for j in range(nbr_nodes):
        pool=node_poolx[j]+boxx*node_pooly[j]
        max_alt[pool]=max(max_alt[pool], node_coords[5*j+2])
        min_alt[pool]=min(min_alt[pool], node_coords[5*j+2])
    min_alt=numpy.floor(min_alt)-1
    max_alt=numpy.ceil(max_alt)+1
    for i in range(boxx*boxy):
        alt_range=max_alt[i]-min_alt[i]
        scal_alt[i]= 771 if alt_range<770 else 1285 if alt_range<1284 else 4369 if alt_range<4368 else 13107
    inv_alt=65535*numpy.ones(boxx*boxy, dtype=numpy.uint16)/scal_alt
    for j in range(nbr_nodes):
        pool=node_poolx[j]+boxx*node_pooly[j]
        node_icoords[5*j+2]=round((node_coords[5*j+2]-min_alt[pool])*inv_alt[pool])
    node_icoords[3::5]=((1+normal_map_strength*node_coords[3::5])/2*65535)
    # BEWARE : normal coordinates are pointing (EAST,SOUTH) in X-Plane, not (EAST,NORTH) ! (cfr DSF specs), so v -> -v
    node_icoords[4::5]=((1-normal_map_strength*node_coords[4::5])/2*65535)
    return (node_icoords, node_poolx,node_pooly,min_alt, scal_alt)
##############################################################################

##############################################################################
def build_dsf(tile,download_queue):
    dsf_file_name=os.path.join(tile.build_dir,'Earth nav data',FNAMES.long_latlon(tile.lat,tile.lon)+'.dsf')
    # 0) Reading custom_zl info
    dico_customzl=zone_list_to_ortho_dico(tile)
    ##########################
    # 0bis) Elevaion for normal maps
    if build_normal_maps:
        try:
            fill_nodata = tile.fill_nodata or "to zero"
            source= ((";" in tile.custom_dem) and tile.custom_dem.split(";")[0]) or tile.custom_dem
            tile.dem=DEM.DEM(tile.lat,tile.lon,source,fill_nodata,info_only=False)
            tile.dem.create_normal_map()
        except Exception as e:
            print(e)
            UI.exit_message_and_bottom_line("\nERROR: Could not determine the appropriate elevation source. Please check your custom_dem entry.")
            return 0
    ###########################        
    # 1) Reading mesh file and building untextured node pools
    UI.vprint(1,"-> Reading mesh file")
    (mesh_version, nbr_nodes, node_coords, nbr_tris, tri_list)=MESH.read_mesh_file(FNAMES.mesh_file(tile.build_dir,tile.lat,tile.lon))
    UI.progress_bar(1,5)
    UI.vprint(1,"-> Building point pools")
    divx=8;boxx=divx+1
    divy=8;boxy=divy+1
    (node_icoords, node_poolx,node_pooly,min_alt, scal_alt)=poolification(nbr_nodes, node_coords, tile.lat, tile.lon, divx, divy, tile.normal_map_strength)
    node_icoords=array.array('H',node_icoords)
    idx_node_to_idx_pool={i:node_poolx[i]+boxx*node_pooly[i] for i in range(nbr_nodes)}
    del(node_poolx);del(node_pooly)
    pool_params={}
    nbr_pools=boxx*boxy
    scalx=1/divx
    scaly=1/divy
    for i in range(nbr_pools):
        pool_params[i]=(scalx, tile.lon+i%boxx*scalx,scaly,tile.lat+(i//boxx)*scaly,scal_alt[i],min_alt[i],2,-1,2,-1,1,0,1,0,1,0,1,0)
        #print(pool_params[i])
    UI.progress_bar(1,10)
    ##########################
    # 2) Preparing for DSF pools, textured nodes and textured tris
    nbr_dsfpools_yet_in=0
    dsfpool={}
    dsfpool_length={}
    dsfpool_planes={}
    dsfpool_params={}
    dico_tmp_idx_dsfpool={}
    # we need more pools for textured nodes than for nodes,
    # one for each number of coordinates [7 (land or experimental water), 9 (water masks) and 5 (X-Plane water)]
    for (pool_planes,idx_pool) in itertools.product((7,5,9),range(nbr_pools)):
        idx_dsfpool=len(dico_tmp_idx_dsfpool)
        dico_tmp_idx_dsfpool[(idx_pool, pool_planes)]=idx_dsfpool
        dsfpool[idx_dsfpool]=array.array('H')
        dsfpool_length[idx_dsfpool]=0
        dsfpool_planes[idx_dsfpool]=pool_planes
        dsfpool_params[idx_dsfpool]=pool_params[idx_pool]
    textured_nodes={}
    len_textured_nodes=0
    textured_tris={}
    total_cross_pool=0
    ##########################
    # 3) Terrains
    dico_terrains={}
    overlay_terrains=set()
    treated_textures=set()
    skipped_terrains_for_masking=set()
    # For future flexibility 
    dico_dsf_def={'bPROP':b'','bTERT':b'','bOBJT':b'','bPOLY':b'','bNETW':b'','bDEMN':b'','bGEOD':b'','bDEMS':b'','bCMDS':b''}
    if min_cliff:
        dico_terrains={'terrain_Water':0, 'terrain_Cliff':1}
        dico_dsf_def['bTERT']=bytes("terrain_Water\0terrain/terrain_Cliff.ter\0",'ascii')
        textured_tris[0] = defaultdict(lambda: array.array('H'))
        textured_tris[1] = defaultdict(lambda: array.array('H'))
        overlay_terrains.add(1)
        total_cliff=0
    else:
        dico_terrains={'terrain_Water':0}
        dico_dsf_def['bTERT']=bytes("terrain_Water\0",'ascii')
        textured_tris[0]=defaultdict(lambda: array.array('H'))
    
    scal_vect=numpy.array([GEO.lon_to_m(tile.lat+0.5),GEO.lat_to_m,1])
    scal_vect_prod=numpy.array([scal_vect[1]*scal_vect[2],scal_vect[2]*scal_vect[0],scal_vect[0]*scal_vect[1]])
    (tri_land, tri_water, tri_sea, tri_cliff) = MESH.sort_tris_by_landuse(tri_list, mesh_version, tile.use_masks_for_inland, node_coords,  min_cliff2, scal_vect_prod)
    del(tri_list)
       
    # Next, we go through the Triangle section of the mesh file and build DSF 
    # mesh points (these take into accound texture as well), point pools, etc. 
    UI.vprint(1,"-> Attribution of terrain(s) to triangles")
    
    def find_terrain_and_encode_tris(tri_list, terrain_finder, pool_planes, coord_encoding):
        nbr_textured_nodes = 0
        nbr_cross_pool_tris = 0
        if isinstance(terrain_finder, str):
            terrain_idx = dico_terrains[terrain_finder]
            terrain_finder = lambda n1, n2, n3, tri_type: (terrain_idx, None)
        for (n1,n2,n3,tri_type) in tri_list:
            (terrain_idx, texture_attributes) = terrain_finder(n1, n2, n3, tri_type)
            if terrain_idx is None: continue
            tri_p=array.array('H')                 
            for n in (n1, n3, n2):     # beware of ordering for orientation ! 
                idx_pool=idx_node_to_idx_pool[n]
                node_hash=(idx_pool,*node_icoords[5*n:5*n+3],terrain_idx)
                if node_hash in textured_nodes:
                    (idx_dsfpool,pos_in_pool)=textured_nodes[node_hash]
                else:
                    idx_pool=idx_node_to_idx_pool[n]
                    idx_dsfpool=dico_tmp_idx_dsfpool[(idx_pool, pool_planes)]
                    nbr_textured_nodes+=1
                    pos_in_pool=dsfpool_length[idx_dsfpool]
                    textured_nodes[node_hash]=(idx_dsfpool,pos_in_pool)
                    coord_encoding(dsfpool[idx_dsfpool],node_icoords,n,texture_attributes)    
                    dsfpool_length[idx_dsfpool]+=1
                    if dsfpool_length[idx_dsfpool]==65536:
                        future_idx_dsfpool=len(dsfpool)
                        dico_tmp_idx_dsfpool[(idx_pool, pool_planes)]=future_idx_dsfpool
                        dsfpool[future_idx_dsfpool]=array.array('H')
                        dsfpool_length[future_idx_dsfpool]=0
                        dsfpool_planes[future_idx_dsfpool]=pool_planes
                        dsfpool_params[future_idx_dsfpool]=pool_params[idx_pool]
                tri_p.extend((idx_dsfpool,pos_in_pool))
            if tri_p[0] == tri_p[2] == tri_p[4]:
                textured_tris[terrain_idx][tri_p[0]].extend((tri_p[1],tri_p[3],tri_p[5]))
            else:
                nbr_cross_pool_tris+=1
                textured_tris[terrain_idx]['cross-pool'].extend(tri_p)
        return (nbr_textured_nodes, nbr_cross_pool_tris)
    
    def ortho_terrain_finder(n1,n2,n3,tri_type):
        (bary_lon,bary_lat)=barycenter(n1,n2,n3,node_coords)
        texture_attributes=dico_customzl[GEO.wgs84_to_orthogrid(bary_lat,bary_lon,tile.mesh_zl)]
        terrain_attributes=(texture_attributes,tri_type)
        if terrain_attributes in dico_terrains: 
            return (dico_terrains[terrain_attributes],texture_attributes)
        else:
            if tri_type==2:
                if terrain_attributes not in skipped_terrains_for_masking:
                    mask_im=MASK.needs_mask(tile,*texture_attributes)
                    if mask_im:
                        UI.vprint(2,"      Use of an alpha mask.")
                        mask_im.save(os.path.join(tile.build_dir,"textures",FNAMES.mask_file(*texture_attributes)))
                    else:
                        skipped_terrains_for_masking.add(terrain_attributes)
                        # clean up potential old masks in the tile dir   
                        try: os.remove(os.path.join(tile.build_dir,"textures",FNAMES.mask_file(*texture_attributes)))
                        except: pass
                        return (None,None)
                else:
                    return (None,None)
            terrain_idx=len(dico_terrains)
            textured_tris[terrain_idx]=defaultdict(lambda: array.array('H'))
            dico_terrains[terrain_attributes]=terrain_idx
            is_overlay=tri_type==2 or (tri_type==1 and not (tile.experimental_water & 1))
            if is_overlay: overlay_terrains.add(terrain_idx)
            texture_file_name=FNAMES.dds_file_name_from_attributes(*texture_attributes)
            if texture_attributes not in treated_textures:
                if (not os.path.isfile(os.path.join(tile.build_dir,'textures',texture_file_name))) or (tri_type==2 and tile.imprint_masks_to_dds):
                    if  'g2xpl' not in texture_attributes[3]:
                        download_queue.put(texture_attributes)
                    elif os.path.isfile(os.path.join(tile.build_dir,'textures',texture_file_name.replace('dds','partial.dds'))):
                        texture_file_name=texture_file_name.replace('dds','partial.dds')
                        UI.vprint(2,"   Texture file "+texture_file_name+" already present.")
                    else:
                        UI.vprint(1,"   Missing a required texture, conversion from g2xpl requires texture download.")
                        download_queue.put(texture_attributes)
                else:
                    UI.vprint(2,"   Texture file "+texture_file_name+" already present.")
                if build_normal_maps:
                    UI.vprint(1,"Building normal map")
                    build_texture_normal_map(tile,texture_attributes)
                    UI.vprint(1,"Done.")
                treated_textures.add(texture_attributes)
            terrain_file_name=create_terrain_file(tile,texture_file_name,*texture_attributes,tri_type,is_overlay)
            dico_dsf_def['bTERT']+=bytes('terrain/'+terrain_file_name+'\0','ascii') 
            return (terrain_idx,texture_attributes)
    
    def low_res_ortho_terrain_finder(n1,n2,n3,tri_type):
        (bary_lon,bary_lat)=barycenter(n1,n2,n3,node_coords)
        (til_x_left,til_y_top)=GEO.wgs84_to_orthogrid(bary_lat,bary_lon,experimental_water_zl)
        texture_attributes=(til_x_left,til_y_top,experimental_water_zl,'SEA')
        terrain_attributes=(texture_attributes,tri_type)
        if terrain_attributes in dico_terrains:
            terrain_idx=dico_terrains[terrain_attributes]
        else:
            terrain_idx=len(dico_terrains)
            is_overlay= not(tile.experimental_water & 2) and 'ratio_water'
            if is_overlay: overlay_terrains.add(terrain_idx)
            textured_tris[terrain_idx]=defaultdict(lambda: array.array('H'))
            dico_terrains[terrain_attributes]=terrain_idx
            texture_file_name=FNAMES.dds_file_name_from_attributes(*texture_attributes)
            # do we need to download a new texture ?       
            if texture_attributes not in treated_textures:
                if not os.path.isfile(os.path.join(tile.build_dir,'textures',texture_file_name)):
                    download_queue.put(texture_attributes)
                else:
                    UI.vprint(1,"   Texture file "+texture_file_name+" already present.")
                treated_textures.add(texture_attributes)
            terrain_file_name=create_terrain_file(tile,texture_file_name,*texture_attributes,tri_type,is_overlay)
            dico_dsf_def['bTERT']+=bytes('terrain/'+terrain_file_name+'\0','ascii') 
        return (terrain_idx,texture_attributes)
        
    def ortho_coord_land_7(arr,node_icoords,n,texture_attributes):
        (s,t)=GEO.st_coord_int(node_coords[5*n+1],node_coords[5*n],*texture_attributes[:-1])
        arr.extend(node_icoords[5*n:5*n+5])
        arr.extend((s,t))
    def ortho_coord_water_7(arr,node_icoords,n,texture_attributes):
        (s,t)=GEO.st_coord_int(node_coords[5*n+1],node_coords[5*n],*texture_attributes[:-1])
        arr.extend(node_icoords[5*n:5*n+5])
        arr.extend((s,t))
    def ortho_coord_sea_7(arr,node_icoords,n,texture_attributes):
        (s,t)=GEO.st_coord_int(node_coords[5*n+1],node_coords[5*n],*texture_attributes[:-1])
        arr.extend(node_icoords[5*n:5*n+5])
        arr.extend((s,t))
    def ortho_coord_sea_9(arr,node_icoords,n,texture_attributes):
        (s,t)=GEO.st_coord_int(node_coords[5*n+1],node_coords[5*n],*texture_attributes[:-1])
        arr.extend(node_icoords[5*n:5*n+5])
        arr.extend((s,t,s,t))
    def ortho_coord_water_9(arr,node_icoords,n,texture_attributes):
        (s,t)=GEO.st_coord_int(node_coords[5*n+1],node_coords[5*n],*texture_attributes[:-1])
        arr.extend(node_icoords[5*n:5*n+5])
        arr.extend((s,t,0,int(round(tile.ratio_water*65535))))
    def coord_water_5(arr,node_icoords,n,texture_attributes=None):
        arr.extend(node_icoords[5*n:5*n+5])
    def coord_cliff_5(arr,node_icoords,n,texture_attributes=None):
        arr.extend(node_icoords[5*n:5*n+5])
    
    # A) Over tri_type=2
    if tile.imprint_masks_to_dds:
        find_terrain_and_encode_tris(tri_sea, ortho_terrain_finder, 7, ortho_coord_sea_7)
    else:
        find_terrain_and_encode_tris(tri_sea, ortho_terrain_finder, 9, ortho_coord_sea_9)
    UI.progress_bar(1,20)
    if tile.experimental_water & 2:
        find_terrain_and_encode_tris(tri_sea, low_res_ortho_terrain_finder, 7, ortho_coord_sea_7)
    else:
        find_terrain_and_encode_tris(tri_sea, "terrain_Water", 5, coord_water_5)
        if tile.add_low_res_sea_ovl:
            find_terrain_and_encode_tris(tri_sea, low_res_ortho_terrain_finder, 9, ortho_coord_water_9)
    UI.progress_bar(1,25)
    # B) Over tri_type=1 
    if tile.experimental_water & 1:
        find_terrain_and_encode_tris(tri_water, ortho_terrain_finder, 7, ortho_coord_water_7)   
    else:
        find_terrain_and_encode_tris(tri_water, "terrain_Water", 5, coord_water_5)
        find_terrain_and_encode_tris(tri_water, ortho_terrain_finder, 9, ortho_coord_water_9)
    UI.progress_bar(1, 40)
    # C) Over tri_type=0
    find_terrain_and_encode_tris(tri_land, ortho_terrain_finder, 7, ortho_coord_land_7)  
    UI.progress_bar(1, 80)
    if min_cliff and tri_cliff:
        find_terrain_and_encode_tris(tri_cliff, "terrain_Cliff", 5, coord_cliff_5)
    UI.progress_bar(1, 90)
    download_queue.put('quit')
    
    UI.vprint(1,"-> Encoding of the DSF file")  
    UI.vprint(1,"     Final nbr of nodes: "+str(len_textured_nodes))
    UI.vprint(2,"     Final nbr of cross pool tris: "+str(total_cross_pool))
    if min_cliff: UI.vprint(2,"     Final nbr of cliff tris: "+str(len(tri_cliff)))

    # 4) Now is time to write our DSF to disk, the exact binary format is described on the wiki
    if os.path.exists(dsf_file_name+'.bak'):
        os.remove(dsf_file_name+'.bak')
    if os.path.exists(dsf_file_name):
        os.rename(dsf_file_name,dsf_file_name+'.bak')
    if min_cliff and textured_tris[1]:
        try:
            shutil.copy(os.path.join(FNAMES.Utils_dir,'terrain_Cliff.ter'),os.path.join(tile.build_dir,'terrain'))
        except:
            pass
  
    
    if not dico_dsf_def['bPROP']:
        dico_dsf_def['PROP']=bytes("sim/west\0"+str(tile.lon)+"\0"+"sim/east\0"+str(tile.lon+1)+"\0"+\
               "sim/south\0"+str(tile.lat)+"\0"+"sim/north\0"+str(tile.lat+1)+"\0"+\
               "sim/creation_agent\0"+"Ortho4XP\0",'ascii')
    else:
        dico_dsf_def['bPROP']+=b'sim/creation_agent\0Patched by Ortho4XP\0'
    # Computation of intermediate and of total length 
    size_of_head_atom=16+len(dico_dsf_def['bPROP'])
    size_of_prop_atom=8+len(dico_dsf_def['bPROP'])
    size_of_defn_atom=48+len(dico_dsf_def['bTERT'])+len(dico_dsf_def['bOBJT'])+len(dico_dsf_def['bPOLY'])+len(dico_dsf_def['bNETW'])+len(dico_dsf_def['bDEMN'])
    size_of_geod_atom=8+len(dico_dsf_def['bGEOD'])
    for k in range(len(dsfpool)):
        if dsfpool_length[k]>0:
            size_of_geod_atom+=21+dsfpool_planes[k]*(9+2*dsfpool_length[k])
    UI.vprint(2,"     Size of DEFN atom : "+str(size_of_defn_atom)+" bytes.")    
    UI.vprint(2,"     Size of GEOD atom : "+str(size_of_geod_atom)+" bytes.")    
    f=open(dsf_file_name+'.tmp','wb')
    f.write(b'XPLNEDSF')
    f.write(struct.pack('<I',1))
    # Head super-atom
    f.write(b"DAEH")
    f.write(struct.pack('<I',size_of_head_atom))
    f.write(b"PORP")
    f.write(struct.pack('<I',size_of_prop_atom))
    f.write(dico_dsf_def['bPROP'])
    # Definitions super-atom
    f.write(b"NFED")
    f.write(struct.pack('<I',size_of_defn_atom))
    f.write(b"TRET")
    f.write(struct.pack('<I',8+len(dico_dsf_def['bTERT'])))
    f.write(dico_dsf_def['bTERT'])
    f.write(b"TJBO")
    f.write(struct.pack('<I',8+len(dico_dsf_def['bOBJT'])))
    f.write(dico_dsf_def['bOBJT'])
    f.write(b"YLOP")
    f.write(struct.pack('<I',8+len(dico_dsf_def['bPOLY'])))
    f.write(dico_dsf_def['bPOLY'])
    f.write(b"WTEN")
    f.write(struct.pack('<I',8+len(dico_dsf_def['bNETW'])))
    f.write(dico_dsf_def['bNETW'])
    f.write(b"NMED")
    f.write(struct.pack('<I',8+len(dico_dsf_def['bDEMN'])))
    f.write(dico_dsf_def['bDEMN'])
    # Geodata super-atom
    f.write(b"DOEG")
    f.write(struct.pack('<I',size_of_geod_atom))
    f.write(dico_dsf_def['bGEOD'])
    for k in range(len(dsfpool)):
        if dsfpool_length[k]==0:
            continue
        f.write(b'LOOP')
        f.write(struct.pack('<I',13+dsfpool_planes[k]+2*dsfpool_planes[k]*dsfpool_length[k]))
        f.write(struct.pack('<I',dsfpool_length[k]))
        f.write(struct.pack('<B',dsfpool_planes[k]))
        for l in range(dsfpool_planes[k]):
            f.write(struct.pack('<B',0))
            for m in range(dsfpool_length[k]):
                f.write(struct.pack('<H',dsfpool[k][dsfpool_planes[k]*m+l]))
    for k in range(len(dsfpool)):
        if dsfpool_length[k]==0:
            continue
        f.write(b'LACS')
        f.write(struct.pack('<I',8+8*dsfpool_planes[k]))
        for l in range(2*dsfpool_planes[k]):
            f.write(struct.pack('<f',dsfpool_params[k][l]))
    UI.progress_bar(1,95)
    if UI.red_flag: UI.vprint(1,"DSF construction interrupted."); return 0   
    # Since we possibly skipped some pools, and since we possibly
    # get pools from elsewhere, we rebuild a dico
    # which tells the pool position in the dsf of a pool prior
    # to the stripping :
    dico_new_dsf_pool={}
    new_idx_dsfpool=nbr_dsfpools_yet_in
    for k in range(len(dsfpool)):
        if dsfpool_length[k] != 0:
            dico_new_dsf_pool[k]=new_idx_dsfpool
            new_idx_dsfpool+=1
    # DEMS atom
    if dico_dsf_def['bDEMS']:
        f.write(b"SMED")
        f.write(struct.pack('<I',8+len(dico_dsf_def['bDEMS'])))
        f.write(dico_dsf_def['bDEMS'])
    # Commands atom
    # we first compute its size :
    size_of_cmds_atom=8+len(dico_dsf_def['bCMDS'])
    for terrain_idx in textured_tris:
        if len(textured_tris[terrain_idx])==0:
            continue
        size_of_cmds_atom+=3
        for idx_dsfpool in textured_tris[terrain_idx]:
            if idx_dsfpool != 'cross-pool':
                size_of_cmds_atom+= 13+2*(len(textured_tris[terrain_idx][idx_dsfpool])+\
                        ceil(len(textured_tris[terrain_idx][idx_dsfpool])/255))
            else:
                size_of_cmds_atom+= 13+2*(len(textured_tris[terrain_idx][idx_dsfpool])+\
                        ceil(len(textured_tris[terrain_idx][idx_dsfpool])/510))
    UI.vprint(2,"     Size of CMDS atom : "+str(size_of_cmds_atom)+" bytes.")
    UI.progress_bar(1,98)
    f.write(b'SDMC')                               # CMDS header 
    f.write(struct.pack('<I',size_of_cmds_atom))   # CMDS length
    f.write(dico_dsf_def['bCMDS'])
    for terrain_idx in textured_tris:
        if len(textured_tris[terrain_idx])==0:
            continue
        #print("terrain_idx = "+str(terrain_idx))
        f.write(struct.pack('<B',4))           # SET DEFINITION 16
        f.write(struct.pack('<H',terrain_idx)) # TERRAIN INDEX
        flag=1 if terrain_idx not in overlay_terrains else 2   # physical or overlay
        lod=-1 if flag==1 else tile.overlay_lod
        for idx_dsfpool in textured_tris[terrain_idx]:
            if idx_dsfpool != 'cross-pool':
                f.write(struct.pack('<B',1))                                 # POOL SELECT
                f.write(struct.pack('<H',dico_new_dsf_pool[idx_dsfpool]))    # POOL INDEX
                
                f.write(struct.pack('<B',18))    # TERRAIN PATCH FLAGS AND LOD
                f.write(struct.pack('<B',flag))  # FLAG
                f.write(struct.pack('<f',0))     # NEAR LOD
                f.write(struct.pack('<f',lod))   # FAR LOD
                
                blocks=floor(len(textured_tris[terrain_idx][idx_dsfpool])/255)
                for j in range(blocks):
                    f.write(struct.pack('<B',23))   # PATCH TRIANGLE
                    f.write(struct.pack('<B',255))  # COORDINATE COUNT

                    for k in range(255):
                        f.write(struct.pack('<H',textured_tris[terrain_idx][idx_dsfpool][255*j+k]))  # COORDINATE IDX
                remaining_tri_p=len(textured_tris[terrain_idx][idx_dsfpool])%255
                if remaining_tri_p != 0:
                    f.write(struct.pack('<B',23))               # PATCH TRIANGLE
                    f.write(struct.pack('<B',remaining_tri_p))  # COORDINATE COUNT
                    for k in range(remaining_tri_p):
                        f.write(struct.pack('<H',textured_tris[terrain_idx][idx_dsfpool][255*blocks+k]))  # COORDINATE IDX
            else:  # idx_dsfpool == 'cross-pool'
                pool_idx_init=textured_tris[terrain_idx][idx_dsfpool][0]
                f.write(struct.pack('<B',1))                                   # POOL SELECT
                f.write(struct.pack('<H',dico_new_dsf_pool[pool_idx_init]))    # POOL INDEX
                f.write(struct.pack('<B',18))    # TERRAIN PATCH FLAGS AND LOD
                f.write(struct.pack('<B',flag))  # FLAG
                f.write(struct.pack('<f',0))     # NEAR LOD
                f.write(struct.pack('<f',lod))   # FAR LOD
                blocks=floor(len(textured_tris[terrain_idx][idx_dsfpool])/510)
                for j in range(blocks):
                    f.write(struct.pack('<B',24))   # PATCH TRIANGLE CROSS-POOL
                    f.write(struct.pack('<B',255))  # COORDINATE COUNT
                    for k in range(255):
                        f.write(struct.pack('<H',dico_new_dsf_pool[textured_tris[terrain_idx][idx_dsfpool][510*j+2*k]]))    # POOL IDX
                        f.write(struct.pack('<H',textured_tris[terrain_idx][idx_dsfpool][510*j+2*k+1]))                     # POS_IN_POOL IDX
                remaining_tri_p=int((len(textured_tris[terrain_idx][idx_dsfpool])%510)/2)
                if remaining_tri_p != 0:
                    f.write(struct.pack('<B',24))               # PATCH TRIANGLE CROSS-POOL
                    f.write(struct.pack('<B',remaining_tri_p))  # COORDINATE COUNT
                    for k in range(remaining_tri_p):
                        f.write(struct.pack('<H',dico_new_dsf_pool[textured_tris[terrain_idx][idx_dsfpool][510*blocks+2*k]]))   # POOL IDX
                        f.write(struct.pack('<H',textured_tris[terrain_idx][idx_dsfpool][510*blocks+2*k+1]))                    # POS_IN_PO0L IDX
    
    if UI.red_flag: UI.vprint(1,"DSF construction interrupted."); return 0   
    f.close()
    f=open(dsf_file_name+'.tmp','rb')
    data=f.read()
    m=hashlib.md5()
    m.update(data)
    md5sum=m.digest()
    f.close()
    f=open(dsf_file_name+'.tmp','ab')
    f.write(md5sum)
    f.close()
    UI.progress_bar(1,100)
    size_of_dsf=28+size_of_head_atom+size_of_defn_atom+size_of_geod_atom+size_of_cmds_atom
    UI.vprint(1,"     DSF file encoded, total size is :",size_of_dsf,"bytes","("+UI.human_print(size_of_dsf)+")")
    return 1
##############################################################################


#######Old Stuff
quad_init_level=3
quad_capacity_high=50000
quad_capacity_low=35000
##############################################################################
def float2qquad(x):
    if x>=1: 
        return '111111111111111111111111'
    return numpy.binary_repr(int(16777216*x)).zfill(24)     # 2**24=16777216
##############################################################################
##############################################################################
class QuadTree(dict):

    class Bucket(dict):
        def __init__(self):
            self['size']=0
            self['idx_nodes']=set()

    def __init__(self,level,bucket_size):
        self.bucket_size=bucket_size
        if level==0:
            self[('','')]=self.Bucket() 
        else:
            for i in range(2**level):
                for j in range(2**level):
                    key=(numpy.binary_repr(i).zfill(level),numpy.binary_repr(j).zfill(level))
                    self[key]=self.Bucket() 
        self.nodes={}
        self.levels={}
        self.last_node=0
    
    def split_bucket(self,key):
        level=len(key[0])+1
        self[(key[0]+'0',key[1]+'0')]=self.Bucket()
        self[(key[0]+'0',key[1]+'1')]=self.Bucket()
        self[(key[0]+'1',key[1]+'0')]=self.Bucket()
        self[(key[0]+'1',key[1]+'1')]=self.Bucket()
        for idx in self[key]['idx_nodes']:
            new_key=(self.nodes[idx][0][:level],self.nodes[idx][1][:level])
            self[new_key]['idx_nodes'].add(idx)
            self[new_key]['size']+=1
            self.levels[idx]+=1
        del(self[key])

    def insert(self,bx,by,level):
        while True:
            key=(bx[:level],by[:level])
            if key in self:
                break
            level+=1
        if self[key]['size']<self.bucket_size:
            self[key]['idx_nodes'].add(self.last_node)
            self[key]['size']+=1
            self.nodes[self.last_node]=(bx,by)
            self.levels[self.last_node]=level
            self.last_node+=1
        else:
            self.split_bucket(key)
            self.insert(bx,by,level+1)
    
    def clean(self):
        for key in list(self.keys()):
            if not self[key]['size']:
                del(self[key])
                
    
    def statistics(self):
        lengths=numpy.array([self[key]['size'] for key in self])
        depths=numpy.array([len(key[0]) for key in self])
        UI.vprint(1,"     Number of buckets:",len(lengths))
        UI.vprint(1,"     Average depth:",depths.mean(),", Average bucket size:",lengths.mean())
        UI.vprint(1,"     Largest depth:",numpy.max(depths))
    
##############################################################################
