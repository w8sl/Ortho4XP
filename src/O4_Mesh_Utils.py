import time
import sys
import os
import pickle
import subprocess
import array
import numpy
import requests
from math import sqrt, cos, pi
from numba import jit
import O4_DEM_Utils as DEM
import O4_UI_Utils as UI
import O4_File_Names as FNAMES
import O4_Geo_Utils as GEO
import O4_Vector_Utils as VECT
import O4_OSM_Utils as OSM
import O4_Version

if 'dar' in sys.platform:
    Triangle4XP_cmd = os.path.join(FNAMES.Utils_dir,"Triangle4XP.app ")
    triangle_cmd    = os.path.join(FNAMES.Utils_dir,"triangle.app ")
    sort_mesh_cmd   = os.path.join(FNAMES.Utils_dir,"moulinette.app ")
    reintroduce_obj_cmd = os.path.join(FNAMES.Utils_dir,"push_obj_into_mesh.app ")
    unzip_cmd       = "7z "
elif 'win' in sys.platform: 
    Triangle4XP_cmd = os.path.join(FNAMES.Utils_dir,"Triangle4XP.exe ")
    triangle_cmd    = os.path.join(FNAMES.Utils_dir,"triangle.exe ")
    sort_mesh_cmd   = os.path.join(FNAMES.Utils_dir,"moulinette.exe ")
    reintroduce_obj_cmd = os.path.join(FNAMES.Utils_dir,"push_obj_into_mesh.exe ")
    unzip_cmd       = os.path.join(FNAMES.Utils_dir,"7z.exe ")
else:
    Triangle4XP_cmd = os.path.join(FNAMES.Utils_dir,"Triangle4XP ")
    triangle_cmd    = os.path.join(FNAMES.Utils_dir,"triangle ")
    sort_mesh_cmd   = os.path.join(FNAMES.Utils_dir,"moulinette ")
    reintroduce_obj_cmd = os.path.join(FNAMES.Utils_dir,"push_obj_into_mesh ")
    unzip_cmd       = "7z "

##############################################################################
@jit(nopython=True)
def is_in_region(lat,lon,latmin,latmax,lonmin,lonmax):
    return lat>=latmin and lat<=latmax and lon>=lonmin and lon<=lonmax
##############################################################################

##############################################################################
def read_mesh_file(mesh_file):
    tmp=open(mesh_file,"r").readlines()
    mesh_version=float(tmp[0].strip().split()[-1])
    nbr_nodes=int(tmp[4])
    arr_coords=array.array('f')
    for item in tmp[5:nbr_nodes+5]:
        arr_coords.extend([float(x) for x in item.split()[:3]])
    arr_normals=array.array('f')
    for item in tmp[nbr_nodes+8:2*nbr_nodes+8]:
        arr_normals.extend([float(x) for x in item.split()[:2]])
    nbr_tris=int(tmp[2*nbr_nodes+10])
    tri_list=[]
    for item in tmp[2*nbr_nodes+11:]:
        # here nodes are referred starting from index 0 (numpy convention versus .mesh or .obj convention)
        (n1,n2,n3,tri_type)=[int(x) for x in item.split()[:4]] 
        tri_list.append((n1-1,n2-1,n3-1,tri_type))
    node_coords=numpy.hstack((numpy.array(arr_coords).reshape((nbr_nodes,3)), numpy.array(arr_normals).reshape((nbr_nodes,2)))).reshape((5*nbr_nodes, ))
    node_coords[2::5]*=100000
    return (mesh_version, nbr_nodes, node_coords, nbr_tris, tri_list)
##############################################################################

##############################################################################
def select_tris_within_region(node_coords, tri_list, latmin, latmax, lonmin, lonmax):
    selected_tris=[]
    for (n1,n2,n3,tri_type) in tri_list:
        (lon,lat) = (node_coords[5*n1:5*n1+2]+node_coords[5*n2:5*n2+2]+node_coords[5*n3:5*n3+2])/3.0
        if is_in_region(lat,lon,latmin,latmax,lonmin,lonmax):
            selected_tris.append((n1,n2,n3,tri_type))
    return selected_tris
##############################################################################

##############################################################################
def extract_mesh_to_linear_wgs84_obj_wavefront(mesh_file, til_x_left, til_y_top, zoomlevel, provider_code): 
    UI.red_flag=False
    timer=time.time()
    (latmax,lonmin)=GEO.gtile_to_wgs84(til_x_left,til_y_top,zoomlevel)
    (latmin,lonmax)=GEO.gtile_to_wgs84(til_x_left+16,til_y_top+16,zoomlevel)
    scalx=GEO.lon_to_m((latmax+latmin)/2)
    scaly=GEO.lat_to_m
    obj_file_name=FNAMES.obj_file(til_x_left,til_y_top,zoomlevel,provider_code)
    mtl_file_name=FNAMES.mtl_file(til_x_left,til_y_top,zoomlevel,provider_code)
    UI.vprint(1,"    Reading mesh file...")
    (mesh_version, nbr_nodes, node_coords, nbr_tris, tri_list) = read_mesh_file(mesh_file)
    UI.vprint(1,"    Selecting triangles inside zone...")
    selected_tris = select_tris_within_region(node_coords, tri_list, latmin, latmax, lonmin, lonmax)
    UI.vprint(1,"    Writing vertices and normals...")
    f=open(obj_file_name,"w")
    f.write("mtllib "+os.path.basename(mtl_file_name)+"\n")
    selected_nodes=array.array('i')
    dico_nodes={}
    nbr_nodes=0
    for (n1,n2,n3,tri_type) in selected_tris:
        if n1 not in dico_nodes:
            nbr_nodes+=1 
            dico_nodes[n1]=nbr_nodes
            selected_nodes.append(n1)
        if n2 not in dico_nodes:
            nbr_nodes+=1 
            dico_nodes[n2]=nbr_nodes
            selected_nodes.append(n2)
        if n3 not in dico_nodes:
            nbr_nodes+=1 
            dico_nodes[n3]=nbr_nodes
            selected_nodes.append(n3)
    for n in selected_nodes:
        f.write("v "+'{:.2f}'.format((node_coords[5*n]-lonmin)*scalx)+" "+\
                '{:.2f}'.format((node_coords[5*n+1]-latmin)*scaly)+" "+\
                '{:.2f}'.format(node_coords[5*n+2])+"\n") 
        f.write("vn "+'{:.2f}'.format(node_coords[5*n+3])+" "+'{:.2f}'.format(node_coords[5*n+4])+" "+\
                      '{:.2f}'.format(sqrt(max(1-node_coords[5*n+3]**2-node_coords[5*n+4]**2,0)))+"\n")
        (s,t)=GEO.st_coord(node_coords[5*n+1],node_coords[5*n],til_x_left,til_y_top,zoomlevel)
        f.write("vt "+'{:.4f}'.format(s)+" "+'{:.4f}'.format(t)+"\n")
    f.write("\n")
    UI.vprint(1,"    Writing faces and materials...")
    selected_tri_list_by_tri_type={}
    for (n1,n2,n3,tri_type) in selected_tris:
        if tri_type not in selected_tri_list_by_tri_type:
            selected_tri_list_by_tri_type[tri_type]=[(n1,n2,n3)]
        else:
            selected_tri_list_by_tri_type[tri_type].append((n1,n2,n3))
    for tri_type in sorted(selected_tri_list_by_tri_type.keys()):
        f.write("usemtl material_"+str(tri_type)+"\n")
        for (n1,n2,n3) in selected_tri_list_by_tri_type[tri_type]:
            f.write("f "+str(dico_nodes[n1])+"/"+str(dico_nodes[n1])+"/"+str(dico_nodes[n1])+" "+\
                         str(dico_nodes[n2])+"/"+str(dico_nodes[n2])+"/"+str(dico_nodes[n2])+" "+\
                         str(dico_nodes[n3])+"/"+str(dico_nodes[n3])+"/"+str(dico_nodes[n3])+"\n")
    f.close()
    # then the mtl file
    f=open(mtl_file_name,'w')
    for tri_type in sorted(selected_tri_list_by_tri_type.keys()):
        f.write("newmtl material_"+str(tri_type)+"\n"+\
            "map_Kd "+FNAMES.geotiff_file_name_from_attributes(til_x_left,til_y_top,zoomlevel,provider_code)+\
            "\n")
    f.close()
    UI.timings_and_bottom_line(timer)
    return
##############################################################################

##############################################################################
def reintroduce_linear_wgs84_obj_wavefront_to_mesh(build_dir, lat, lon, til_x_left, til_y_top, zoomlevel): 
    UI.red_flag=False
    timer=time.time()
    (latmax,lonmin)=GEO.gtile_to_wgs84(til_x_left, til_y_top, zoomlevel)
    (latmin,lonmax)=GEO.gtile_to_wgs84(til_x_left+16, til_y_top+16, zoomlevel)
    scalx=GEO.lon_to_m((latmax+latmin)/2)
    scaly=GEO.lat_to_m
    eps = 1e-6
    (til_x_min, til_y_min) = GEO.wgs84_to_orthogrid(lat+1-eps, lon + eps, zoomlevel)
    (til_x_max, til_y_max) = GEO.wgs84_to_orthogrid(lat + eps, lon+1-eps, zoomlevel)
    print(til_x_min,til_x_left,til_x_max,til_y_min,til_y_top,til_y_max)
    position = (til_x_left - til_x_min)//16 + (til_y_top - til_y_min)//16 * ((til_x_max - til_x_min)//16 + 1)
    mesh_file_name = FNAMES.mesh_file(build_dir, lat, lon) 
    obj_file_name = FNAMES.reintro_obj_file(build_dir, til_x_left, til_y_top, zoomlevel)
    cmd=[reintroduce_obj_cmd.strip(),
              mesh_file_name.strip(),
              str(zoomlevel),
              obj_file_name.strip(),
              '{:.9g}'.format(lonmin),
              '{:.9g}'.format(latmin),
              '{:.9g}'.format(0),
              '{:.9g}'.format(1/scalx),
              '{:.9g}'.format(1/scaly),
              '{:.9g}'.format(1/100000),
              str(position)
              ]
    UI.vprint(1,"-> Start of reintroduction algorithm.")
    UI.vprint(2,'   Reintrocution command:',' '.join(cmd))
    fingers_crossed=subprocess.Popen(cmd,stdout=subprocess.PIPE,bufsize=0)
    while True:
        line = fingers_crossed.stdout.readline()
        if not line: 
            break
        else:
            try:
                print(line.decode("utf-8")[:-1])
            except:
                pass
    time.sleep(0.3)
    fingers_crossed.poll()        
    if fingers_crossed.returncode:
        UI.vprint(0,"\nERROR!!!")
        return 0
    UI.timings_and_bottom_line(timer)
    return
##############################################################################

##############################################################################
@jit(nopython=True)
def tri_is_cliff(n1, n2, n3, node_coords,  min_cliff2, scal_vect_prod):
    nx=(node_coords[5*n2+1]-node_coords[5*n1+1])*(node_coords[5*n3+2]-node_coords[5*n1+2])-(node_coords[5*n3+1]-node_coords[5*n1+1])*(node_coords[5*n2+2]-node_coords[5*n1+2])
    ny=(node_coords[5*n2+2]-node_coords[5*n1+2])*(node_coords[5*n3]-node_coords[5*n1])-(node_coords[5*n3+2]-node_coords[5*n1+2])*(node_coords[5*n2]-node_coords[5*n1])
    nz=(node_coords[5*n2]-node_coords[5*n1])*(node_coords[5*n3+1]-node_coords[5*n1+1])-(node_coords[5*n3]-node_coords[5*n1])*(node_coords[5*n2+1]-node_coords[5*n1+1])
    nx*=scal_vect_prod[0]
    ny*=scal_vect_prod[1]
    nz*=scal_vect_prod[2]
    norm2=nx*nx+ny*ny+nz*nz
    if norm2>=1e-2:
        return abs(nz*nz/norm2) < min_cliff2
    else:
        return False    
##############################################################################

##############################################################################
def sort_tris_by_landuse(tri_list, mesh_version, use_masks_for_inland, node_coords,  min_cliff2, scal_vect_prod):
    water_tri_is_cliff2 = 0.64  # if the (square of the) z component of the unit normal to a water tri is smaller than sea_tri_is_cliff2, it is turned back to a land tri 
    has_water = 7 if mesh_version >= 1.3 else 3
    tri_land = []
    tri_water = []
    tri_sea = []
    tri_cliff = []
    for (n1,n2,n3,tri_type) in tri_list:
        tri_type = (tri_type & has_water) and (2 * ((tri_type & has_water) > 1 or use_masks_for_inland) or 1)
        if tri_type and tri_is_cliff(n1, n2, n3, node_coords, water_tri_is_cliff2, scal_vect_prod):
            tri_type = 0
        if not tri_type:
            tri_land.append((n1, n2 ,n3 , tri_type))
        elif tri_type==1:
            tri_water.append((n1, n2, n3, tri_type))
        else:
            tri_sea.append((n1, n2, n3, tri_type))
    if min_cliff2:
        for (n1,n2,n3,tri_type) in tri_land:
            if tri_is_cliff(n1, n2, n3, node_coords, min_cliff2, scal_vect_prod):
                tri_cliff.append((n1, n2, n3, tri_type))
    return (tuple(tri_land), tuple(tri_water), tuple(tri_sea), tuple(tri_cliff))   
##############################################################################

##############################################################################
def read_objwavefront_file(obj_file,vertex_index_shift=0):
    tmp=open(obj_file,"r").readlines()
    curr_mat=None
    
    arr_coords=array.array('f')
    arr_normals=array.array('f')
    arr_uvcoords=array.array('f')
    i=0
    for line in tmp:
        ty=line[:2]
        if ty=='v ':
            arr_coords.extend([float(x) for x in line.split()[1:4]])        
        elif ty=='vn':
            arr_normals.extend([float(x) for x in line.split()[1:3]])    
        elif ty=='vt':
            arr_uvcoords.extend([float(x) for x in line.split()[1:3]])
        elif ty=='us':
            curr_mat=line.split()[1]
        elif ty=='f ':
            break
        i+=1
    for line in tmp[i:]:
        ty=line[:2]
        if ty=='f ':
            (n1,n2,n3,tri_type)=[int(x) for x in line.split()[:4]] 
        elif ty=='us':
            curr_mat=line.split()[1]
            print(curr_mat)
        
    #node_coords=numpy.hstack((numpy.array(arr_coords).reshape((nbr_nodes,3)), numpy.array(arr_normals).reshape((nbr_nodes,2)))).reshape((5*nbr_nodes, ))
    #node_coords[2::5]*=100000
    return #(mesh_version, nbr_nodes, node_coords, nbr_tris, tri_list)
##############################################################################

##############################################################################
def build_curv_tol_weight_map(tile,weight_array):
    curvature_tol  = tile.curvature_tol[tile.iterate]  if len(tile.curvature_tol)>tile.iterate  else tile.curvature_tol[0]
    apt_curv_tol   = tile.apt_curv_tol[tile.iterate]   if len(tile.apt_curv_tol)>tile.iterate   else tile.apt_curv_tol[0]
    apt_curv_ext   = tile.apt_curv_ext[tile.iterate]   if len(tile.apt_curv_ext)>tile.iterate   else tile.apt_curv_ext[0]
    coast_curv_tol = tile.coast_curv_tol[tile.iterate] if len(tile.coast_curv_tol)>tile.iterate else tile.coast_curv_tol[0]
    coast_curv_ext = tile.coast_curv_ext[tile.iterate] if len(tile.coast_curv_ext)>tile.iterate else tile.coast_curv_ext[0]
    if apt_curv_tol!=curvature_tol and apt_curv_tol>0:
        UI.vprint(1,"-> Modifying curv_tol weight map according to runway locations.")
        try:
            f=open(FNAMES.apt_file(tile),'rb')
            dico_airports=pickle.load(f)
            f.close()
        except:
            UI.vprint(1,"   WARNING: File",FNAMES.apt_file(tile),"is missing (erased after Step 1?), cannot check airport info for upgraded zoomlevel.")
            dico_airports={}
        for airport in dico_airports:
            (xmin,ymin,xmax,ymax)=dico_airports[airport]['boundary'].bounds
            x_shift=1000*apt_curv_ext*GEO.m_to_lon(tile.lat) 
            y_shift=1000*apt_curv_ext*GEO.m_to_lat
            colmin=max(round((xmin-x_shift)*1000),0)
            colmax=min(round((xmax+x_shift)*1000),1000)
            rowmax=min(round(((1-ymin)+y_shift)*1000),1000)
            rowmin=max(round(((1-ymax)-y_shift)*1000),0)
            weight_array[rowmin:rowmax+1,colmin:colmax+1]=curvature_tol/apt_curv_tol 
    if coast_curv_tol!=curvature_tol:
        UI.vprint(1,"-> Modifying curv_tol weight map according to coastline location.")
        sea_layer=OSM.OSM_layer()
        custom_coastline=FNAMES.custom_coastline(tile.lat, tile.lon)
        custom_coastline_dir=FNAMES.custom_coastline_dir(tile.lat, tile.lon)
        if os.path.isfile(custom_coastline):
            UI.vprint(1,"    * User defined custom coastline data detected.")
            sea_layer.update_dicosm(custom_coastline,input_tags=None,target_tags=None)
        elif os.path.isdir(custom_coastline_dir):
            UI.vprint(1,"    * User defined custom coastline data detected (multiple files).")
            for osm_file in os.listdir(custom_coastline_dir):
                UI.vprint(2,"      ",osm_file)
                sea_layer.update_dicosm(os.path.join(custom_coastline_dir,osm_file),input_tags=None,target_tags=None)
                sea_layer.write_to_file(custom_coastline)
        else:
            queries=['way["natural"="coastline"]']    
            tags_of_interest=[]
            if not OSM.OSM_queries_to_OSM_layer(queries,sea_layer,tile.lat,tile.lon,tags_of_interest,cached_suffix='coastline'):
                return 0
        for nodeid in sea_layer.dicosmn:
            (lonp,latp)=[float(x) for x in sea_layer.dicosmn[nodeid]]
            if lonp<tile.lon or lonp>tile.lon+1 or latp<tile.lat or latp>tile.lat+1: continue
            x_shift=1000*coast_curv_ext*GEO.m_to_lon(tile.lat)
            y_shift=coast_curv_ext/(111.12)
            colmin=max(round((lonp-tile.lon-x_shift)*1000),0)
            colmax=min(round((lonp-tile.lon+x_shift)*1000),1000)
            rowmax=min(round((tile.lat+1-latp+y_shift)*1000),1000)
            rowmin=max(round((tile.lat+1-latp-y_shift)*1000),0)
            weight_array[rowmin:rowmax+1,colmin:colmax+1]=numpy.maximum(weight_array[rowmin:rowmax+1,colmin:colmax+1],curvature_tol/coast_curv_tol) 
        del(sea_layer)
    # It could be of interest to write the weight file as a png for user editing    
    #from PIL import Image
    #Image.fromarray((weight_array!=1).astype(numpy.uint8)*255).save('weight.png')
    return
##############################################################################

##############################################################################
def post_process_nodes_altitudes(tile):
    dico_attributes=VECT.Vector_Map.dico_attributes 
    f_node = open(FNAMES.output_node_file(tile),'r')
    init_line_f_node=f_node.readline()
    nbr_pt=int(init_line_f_node.split()[0])
    vertices=numpy.zeros(6*nbr_pt)   
    UI.vprint(1,"-> Loading of the mesh computed by Triangle4XP.")
    for i in range(0,nbr_pt):
        vertices[6*i:6*i+6]=[float(x) for x in f_node.readline().split()[1:7]]
    end_line_f_node=f_node.readline()
    f_node.close()
    UI.vprint(1,"-> Post processing of altitudes according to vector data")
    f_ele  = open(FNAMES.output_ele_file(tile),'r')
    nbr_tri= int(f_ele.readline().split()[0])
    water_tris=set()
    sea_tris=set()
    interp_alt_tris=set()
    for i in range(nbr_tri):
        line = f_ele.readline()
        # 0 typed triangles do not require post-treatment
        if line[-3:-1]==' 0': continue  
        (v1,v2,v3,attr)=[int(x)-1 for x in line.split()[1:5]]
        attr+=1
        if attr >= dico_attributes['INTERP_ALT']: 
            interp_alt_tris.add((v1,v2,v3))
        elif attr & dico_attributes['SEA']:
            sea_tris.add((v1,v2,v3))
        elif attr & dico_attributes['WATER'] or attr & dico_attributes['SEA_EQUIV']:
            water_tris.add((v1,v2,v3))
    if tile.water_smoothing:
        UI.vprint(1,"   Smoothing inland water.")
        for j in range(tile.water_smoothing):   
            for (v1,v2,v3) in water_tris:
                    zmean=(vertices[6*v1+2]+vertices[6*v2+2]+vertices[6*v3+2])/3
                    vertices[6*v1+2]=zmean
                    vertices[6*v2+2]=zmean
                    vertices[6*v3+2]=zmean
    UI.vprint(1,"   Smoothing of sea water.")
    for (v1,v2,v3) in sea_tris:
            if tile.sea_smoothing_mode=='zero':
                vertices[6*v1+2]=0
                vertices[6*v2+2]=0
                vertices[6*v3+2]=0
            elif tile.sea_smoothing_mode=='mean':
                zmean=(vertices[6*v1+2]+vertices[6*v2+2]+vertices[6*v3+2])/3
                vertices[6*v1+2]=zmean
                vertices[6*v2+2]=zmean
                vertices[6*v3+2]=zmean
            else:
                vertices[6*v1+2]=max(vertices[6*v1+2],0)
                vertices[6*v2+2]=max(vertices[6*v2+2],0)
                vertices[6*v3+2]=max(vertices[6*v3+2],0)
    UI.vprint(1,"   Treatment of airports, roads and patches.")
    for (v1,v2,v3) in interp_alt_tris:
            vertices[6*v1+2]=vertices[6*v1+5]
            vertices[6*v2+2]=vertices[6*v2+5]
            vertices[6*v3+2]=vertices[6*v3+5]
            vertices[6*v1+3]=0
            vertices[6*v2+3]=0
            vertices[6*v3+3]=0
            vertices[6*v1+4]=0
            vertices[6*v2+4]=0
            vertices[6*v3+4]=0
    UI.vprint(1,"-> Writing output nodes file.") 
    timer=time.time()    
    f_node = open(FNAMES.output_node_file(tile),'w')
    f_node.write(init_line_f_node)
    for i in range(0,nbr_pt):
        f_node.write(str(i+1)+" "+' '.join(('{:.15f}'.format(x) for x in vertices[6*i:6*i+6]))+"\n")
    f_node.write(end_line_f_node)
    f_node.close()
    print("Elapsed time",time.time()-timer)
    return vertices
##############################################################################

##############################################################################
def write_mesh_file(tile,vertices):
    UI.vprint(1,"-> Writing final mesh to the file "+FNAMES.mesh_file(tile.build_dir,tile.lat,tile.lon))
    timer=time.time()
    f_ele  = open(FNAMES.output_ele_file(tile),'r')
    nbr_vert=len(vertices)//6
    nbr_tri=int(f_ele.readline().split()[0])
    f=open(FNAMES.mesh_file(tile.build_dir,tile.lat,tile.lon),"w")
    f.write("MeshVersionFormatted "+O4_Version.version+"\n")
    f.write("Dimension 3\n\n")
    f.write("Vertices\n")
    f.write(str(nbr_vert)+"\n")
    for i in range(0,nbr_vert):
        f.write('{:.7f}'.format(vertices[6*i]+tile.lon)+" "+\
                '{:.7f}'.format(vertices[6*i+1]+tile.lat)+" "+\
                '{:.7f}'.format(vertices[6*i+2]/100000)+" 0\n") 
    print("Elapsed time:",time.time()-timer)            
    f.write("\n")
    f.write("Normals\n")
    f.write(str(nbr_vert)+"\n")
    for i in range(0,nbr_vert):
        f.write('{:.2f}'.format(vertices[6*i+3])+" "+\
                '{:.2f}'.format(vertices[6*i+4])+"\n")
    f.write("\n")
    print("Elapsed time:",time.time()-timer)
    f.write("Triangles\n")
    f.write(str(nbr_tri)+"\n")
    for i in range(0,nbr_tri):
       f.write(' '.join(f_ele.readline().split()[1:])+"\n")
    f_ele.close()
    f.close()
    print("Elapsed time:",time.time()-timer)
    return
##############################################################################

##############################################################################
# Build a textured .obj wavefront over the extent of an orthogrid cell
##############################################################################
def extract_mesh_to_obj(mesh_file,til_x_left,til_y_top,zoomlevel,provider_code): 
    UI.red_flag=False
    timer=time.time()
    (latmax,lonmin)=GEO.gtile_to_wgs84(til_x_left,til_y_top,zoomlevel)
    (latmin,lonmax)=GEO.gtile_to_wgs84(til_x_left+16,til_y_top+16,zoomlevel)
    obj_file_name=FNAMES.obj_file(til_x_left,til_y_top,zoomlevel,provider_code)
    mtl_file_name=FNAMES.mtl_file(til_x_left,til_y_top,zoomlevel,provider_code)
    f_mesh=open(mesh_file,"r")
    for i in range(4):
        f_mesh.readline()
    nbr_pt_in=int(f_mesh.readline())
    UI.vprint(1,"    Reading nodes...")
    pt_in=numpy.zeros(5*nbr_pt_in,'float')
    for i in range(nbr_pt_in):
        pt_in[5*i:5*i+3]=[float(x) for x in f_mesh.readline().split()[:3]]
    for i in range(3):
        f_mesh.readline()
    for i in range(nbr_pt_in):
        pt_in[5*i+3:5*i+5]=[float(x) for x in f_mesh.readline().split()[:2]]
    for i in range(0,2): # skip 2 lines
        f_mesh.readline()
    if UI.red_flag: UI.exit_message_and_bottom_line(); return 0
    UI.vprint(1,"    Reading triangles...")
    nbr_tri_in=int(f_mesh.readline()) # read nbr of tris
    textured_nodes={}
    textured_nodes_inv={}
    nodes_st_coord={}
    len_textured_nodes=0
    dico_new_tri={}
    len_dico_new_tri=0
    for i in range(0,nbr_tri_in):
        (n1,n2,n3)=[int(x)-1 for x in f_mesh.readline().split()[:3]]
        (lon1,lat1,z1,u1,v1)=pt_in[5*n1:5*n1+5]
        (lon2,lat2,z2,u2,v2)=pt_in[5*n2:5*n2+5]
        (lon3,lat3,z3,u3,v3)=pt_in[5*n3:5*n3+5]
        if is_in_region((lat1+lat2+lat3)/3.0,(lon1+lon2+lon3)/3.0,latmin,latmax,lonmin,lonmax):
            if n1 not in textured_nodes_inv:
                len_textured_nodes+=1 
                textured_nodes_inv[n1]=len_textured_nodes
                textured_nodes[len_textured_nodes]=n1
                nodes_st_coord[len_textured_nodes]=GEO.st_coord(lat1,lon1,til_x_left,til_y_top,zoomlevel,provider_code)
            n1new=textured_nodes_inv[n1]
            if n2 not in textured_nodes_inv:
                len_textured_nodes+=1 
                textured_nodes_inv[n2]=len_textured_nodes
                textured_nodes[len_textured_nodes]=n2
                nodes_st_coord[len_textured_nodes]=GEO.st_coord(lat2,lon2,til_x_left,til_y_top,zoomlevel,provider_code)
            n2new=textured_nodes_inv[n2]
            if n3 not in textured_nodes_inv:
                len_textured_nodes+=1 
                textured_nodes_inv[n3]=len_textured_nodes
                textured_nodes[len_textured_nodes]=n3
                nodes_st_coord[len_textured_nodes]=GEO.st_coord(lat3,lon3,til_x_left,til_y_top,zoomlevel,provider_code)
            n3new=textured_nodes_inv[n3]
            dico_new_tri[len_dico_new_tri]=(n1new,n2new,n3new)
            len_dico_new_tri+=1
    nbr_vert=len_textured_nodes
    nbr_tri=len_dico_new_tri
    if UI.red_flag: UI.exit_message_and_bottom_line(); return 0
    UI.vprint(1,"    Writing the obj file.")
    # first the obj file
    f=open(obj_file_name,"w")
    for i in range(1,nbr_vert+1):
        j=textured_nodes[i]
        f.write("v "+'{:.9f}'.format(pt_in[5*j]-lonmin)+" "+\
                '{:.9f}'.format(pt_in[5*j+1]-latmin)+" "+\
                '{:.9f}'.format(pt_in[5*j+2])+"\n") 
    f.write("\n")
    for i in range(1,nbr_vert+1):
        j=textured_nodes[i]
        f.write("vn "+'{:.9f}'.format(pt_in[5*j+3])+" "+'{:.9f}'.format(pt_in[5*j+4])+" "+'{:.9f}'.format(sqrt(max(1-pt_in[5*j+3]**2-pt_in[5*j+4]**2,0)))+"\n")
    f.write("\n")
    for i in range(1,nbr_vert+1):
        j=textured_nodes[i]
        f.write("vt "+'{:.9f}'.format(nodes_st_coord[i][0])+" "+\
                '{:.9f}'.format(nodes_st_coord[i][1])+"\n")
    f.write("\n")
    f.write("usemtl orthophoto\n\n")
    for i in range(0,nbr_tri):
        (one,two,three)=dico_new_tri[i]
        f.write("f "+str(one)+"/"+str(one)+"/"+str(one)+" "+str(two)+"/"+str(two)+"/"+str(two)+" "+str(three)+"/"+str(three)+"/"+str(three)+"\n")
    f_mesh.close()
    f.close()
    # then the mtl file
    f=open(mtl_file_name,'w')
    f.write("newmtl orthophoto\nmap_Kd "+FNAMES.geotiff_file_name_from_attributes(til_x_left,til_y_top,zoomlevel,provider_code)+"\n")
    f.close()
    UI.timings_and_bottom_line(timer)
    return
##############################################################################




##############################################################################
def build_mesh(tile):
    if UI.is_working: return 0
    UI.is_working=1
    UI.red_flag=False  
    VECT.scalx=cos((tile.lat+0.5)*pi/180)  
    UI.logprint("Step 2 for tile lat=",tile.lat,", lon=",tile.lon,": starting.")
    UI.vprint(0,"\nStep 2 : Building mesh for tile "+FNAMES.short_latlon(tile.lat,tile.lon)+" : \n--------\n")
    UI.progress_bar(1,0)
    poly_file    = FNAMES.input_poly_file(tile)
    node_file    = FNAMES.input_node_file(tile)
    alt_file     = FNAMES.alt_file(tile)
    weight_file  = FNAMES.weight_file(tile)
    if not os.path.isfile(node_file):
        UI.exit_message_and_bottom_line("\nERROR: Could not find ",node_file)
        return 0
    if not tile.iterate and not os.path.isfile(poly_file):
        UI.exit_message_and_bottom_line("\nERROR: Could not find ",poly_file)
        return 0
    fill_nodata = (tile.fill_nodata or "to zero") if not tile.iterate else False
    if not os.path.isfile(alt_file):
        UI.exit_message_and_bottom_line("\nERROR: Could not find",alt_file,". You must run Step 1 first.")
        return 0
    try:
        source= ((";" in tile.custom_dem) and tile.custom_dem.split(";")[tile.iterate]) or tile.custom_dem
        tile.dem=DEM.DEM(tile.lat,tile.lon,source,fill_nodata,info_only=True)
        if not os.path.getsize(alt_file)==4*tile.dem.nxdem*tile.dem.nydem:
            UI.exit_message_and_bottom_line("\nERROR: Cached raster elevation does not match the current custom DEM specs.\n       You must run Step 1 and Step 2 with the same elevation base.")
            return 0
    except Exception as e:
        print(e)
        UI.exit_message_and_bottom_line("\nERROR: Could not determine the appropriate source. Please check your custom_dem entry.")
        return 0
    try:
        f=open(node_file,'r')
        input_nodes=int(f.readline().split()[0])
        f.close()
    except:
        UI.exit_message_and_bottom_line("\nERROR: In reading ",node_file)
        return 0
        
    timer=time.time()
    tri_verbosity = 'Q' if UI.verbosity<=1 else 'V'
    output_poly   = 'P' if UI.cleaning_level else ''
    do_refine     = 'r' if tile.iterate else 'A'
    limit_tris    = 'S'+str(max(int(tile.limit_tris/1.9-input_nodes),0)) if tile.limit_tris else ''
    Tri_option    = '-p'+do_refine+'uYB'+tri_verbosity+output_poly+limit_tris
    
    
    weight_array=numpy.ones((1001,1001),dtype=numpy.float32)
    build_curv_tol_weight_map(tile,weight_array)
    weight_array.tofile(weight_file)
    del(weight_array)
    
    #curv_tol_scaling=sqrt(tile.dem.nxdem/(1000*(tile.dem.x1-tile.dem.x0)))
    curv_tol_scaling=100
    curvature_tol=tile.curvature_tol[tile.iterate] if len(tile.curvature_tol)>tile.iterate else tile.curvature_tol[0]
    hmin=tile.hmin[tile.iterate] if len(tile.hmin)>tile.iterate else tile.hmin[0]
    hmin_effective=max(hmin,(tile.dem.y1-tile.dem.y0)*GEO.lat_to_m/tile.dem.nydem/2)
    min_angle=tile.min_angle[tile.iterate] if len(tile.min_angle)>tile.iterate else tile.min_angle[0]
    mesh_cmd=[Triangle4XP_cmd.strip(),
              Tri_option.strip(),
              '{:.9g}'.format(GEO.lon_to_m(tile.lat)),
              '{:.9g}'.format(GEO.lat_to_m),
              '{:n}'.format(tile.dem.nxdem),
              '{:n}'.format(tile.dem.nydem),
              '{:.9g}'.format(tile.dem.x0),
              '{:.9g}'.format(tile.dem.y0),
              '{:.9g}'.format(tile.dem.x1),
              '{:.9g}'.format(tile.dem.y1),
              '{:.9g}'.format(tile.dem.nodata),
              '{:.9g}'.format(curvature_tol*curv_tol_scaling),
              '{:.9g}'.format(min_angle),str(hmin_effective),alt_file,weight_file,poly_file]
    
    del(tile.dem) # for machines with not much RAM, we do not need it anymore
    tile.dem=None
    UI.vprint(1,"-> Start of the mesh algorithm Triangle4XP.")
    UI.vprint(2,'   Mesh command:',' '.join(mesh_cmd))
    fingers_crossed=subprocess.Popen(mesh_cmd,stdout=subprocess.PIPE,bufsize=0)
    while True:
        line = fingers_crossed.stdout.readline()
        if not line: 
            break
        else:
            try:
                print(line.decode("utf-8")[:-1])
            except:
                pass
    time.sleep(0.3)
    fingers_crossed.poll()        
    if fingers_crossed.returncode:
        UI.vprint(0,"\nWARNING: Triangle4XP could not achieve the requested quality (min_angle), most probably due to an uncatched OSM error.\n"+\
                    "It will be tempted now with no angle constraint (i.e. min_angle=0).")
        mesh_cmd[-5]='{:.9g}'.format(0)
        fingers_crossed=subprocess.Popen(mesh_cmd,stdout=subprocess.PIPE,bufsize=0)
        while True:
            line = fingers_crossed.stdout.readline()
            if not line: 
                break
            else:
                try:
                    print(line.decode("utf-8")[:-1])
                except:
                    pass
        time.sleep(0.3)
        fingers_crossed.poll()
        if fingers_crossed.returncode:
            UI.exit_message_and_bottom_line("\nERROR: Triangle4XP really couldn't make it !\n\n"+\
                                        "If the reason is not due to the limited amount of RAM please\n"+\
                                        "file a bug including the .node and .poly files that you\n"+\
                                        "will find in "+str(tile.build_dir)+".\n")
            return 0
        
    if UI.red_flag: UI.exit_message_and_bottom_line(); return 0
    
    vertices=post_process_nodes_altitudes(tile)

    if UI.red_flag: UI.exit_message_and_bottom_line(); return 0
    
    write_mesh_file(tile,vertices)
    #
    if UI.cleaning_level:
        try: os.remove(FNAMES.weight_file(tile))
        except: pass
        try: os.remove(FNAMES.output_node_file(tile))
        except: pass
        try: os.remove(FNAMES.output_ele_file(tile))
        except: pass
    if UI.cleaning_level>2:
        try: os.remove(FNAMES.alt_file(tile))
        except: pass
        try: os.remove(FNAMES.input_node_file(tile))
        except: pass
        try: os.remove(FNAMES.input_poly_file(tile))
        except: pass
    
    UI.timings_and_bottom_line(timer)
    UI.logprint("Step 2 for tile lat=",tile.lat,", lon=",tile.lon,": normal exit.")
    return 1
##############################################################################

##############################################################################
def sort_mesh(tile):
    if UI.is_working: return 0
    UI.is_working=1
    UI.red_flag=False  
    mesh_file = FNAMES.mesh_file(tile.build_dir,tile.lat,tile.lon)
    if not os.path.isfile(mesh_file):
        UI.exit_message_and_bottom_line("\nERROR: Could not find ",mesh_file)
        return 0
    sort_mesh_cmd_list=[sort_mesh_cmd.strip(),str(tile.default_zl),mesh_file]
    UI.vprint(1,"-> Reorganizing mesh triangles.")
    timer=time.time()
    moulinette=subprocess.Popen(sort_mesh_cmd_list,stdout=subprocess.PIPE,bufsize=0)
    while True:
        line = moulinette.stdout.readline()
        if not line: 
            break
        else:
            print(line.decode("utf-8")[:-1])
    UI.timings_and_bottom_line(timer)
    UI.logprint("Moulinette applied for tile lat=",tile.lat,", lon=",tile.lon," and ZL",tile.default_zl)
    return 1
##############################################################################

##############################################################################
def triangulate(name,path_to_Ortho4XP_dir):
    Tri_option = ' -pAYPQ '
    mesh_cmd=[os.path.join(path_to_Ortho4XP_dir,triangle_cmd).strip(),Tri_option.strip(),name+'.poly']
    fingers_crossed=subprocess.Popen(mesh_cmd,stdout=subprocess.PIPE,bufsize=0)
    while True:
        line = fingers_crossed.stdout.readline()
        if not line: 
            break
        else:
            print(line.decode("utf-8")[:-1])
    fingers_crossed.poll()        
    if fingers_crossed.returncode:
        print("\nERROR: triangle crashed, check osm mask data.\n")
        return 0
    return 1
##############################################################################   

##############################################################################   
community_server=False
if os.path.exists(os.path.join(FNAMES.Ortho4XP_dir,"community_server.txt")):
    try:
        f=open(os.path.join(FNAMES.Ortho4XP_dir,"community_server.txt"),'r')
        for line in f.readlines():
            line=line.strip()
            if not line: continue
            if '#' in line:
               if line[0]=='#': continue
               else: line=line.split('#')[0].strip()
            if not line: continue
            community_server=True
            community_prefix=line
            break
    except:
        pass
##############################################################################
def community_mesh(tile):
    if not community_server:
        UI.exit_message_and_bottom_line("\nERROR: No community server defined in community_server.txt")
        return 0
    url=community_prefix+os.path.basename(FNAMES.mesh_file(tile.build_dir,tile.lat,tile.lon))+'.7z'
    timer=time.time()
    UI.vprint(0,"Querying",url,"...")
    try:
        r=requests.get(url,timeout=30)
        if '[200]' in str(r):
            UI.vprint(0,"We've got something !")
            f=open(FNAMES.mesh_file(tile.build_dir,tile.lat,tile.lon)+'.7z','wb')
            f.write(r.content)
            f.close()
            if subprocess.call([unzip_cmd.strip(),'e','-y','-o'+tile.build_dir,FNAMES.mesh_file(tile.build_dir,tile.lat,tile.lon)+".7z"]):
                UI.exit_message_and_bottom_line("\nERROR: Could not extract community_mesh from archive.")
                return 0
            os.remove(FNAMES.mesh_file(tile.build_dir,tile.lat,tile.lon)+'.7z')
            UI.timings_and_bottom_line(timer)
            return 1
        elif '[40' in str(r):
            UI.exit_message_and_bottom_line("\nSORRY: Community server does not propose that mesh: "+str(r))
            return 0
        elif '[50' in str(r):
            UI.exit_message_and_bottom_line("\nSORRY: Community server seems to be down or struggling: "+str(r))
            return 0
        else:
            UI.exit_message_and_bottom_line("\nSORRY: Community server seems to be down or struggling: "+str(r))
            return 0
    except Exception as e:
        UI.exit_message_and_bottom_line("\nERROR: Network or server unreachable:\n"+str(e))
        return 0
##############################################################################        

