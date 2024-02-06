all: images/gello-ar4.png \
	3dprint_parts/ring.stl \
	3dprint_parts/l1.stl \
	3dprint_parts/arm1.stl \
	3dprint_parts/arm2.stl \
	3dprint_parts/wrist.stl \

images/gello-ar4.png: gello-ar4.scad
	openscad -o images/gello-ar4.png --imgsize=1600,1600 gello-ar4.scad
	

3dprint_parts/ring.stl: ring.scad
	openscad -o 3dprint_parts/ring.stl ring.scad
	
3dprint_parts/l1.stl: ring.scad
	openscad -o 3dprint_parts/l1.stl l1.scad
	
3dprint_parts/arm1.stl: arm1.scad
	openscad -o 3dprint_parts/arm1.stl arm1.scad
	
3dprint_parts/arm2.stl: arm1.scad
	openscad -o 3dprint_parts/arm2.stl arm2.scad
	
3dprint_parts/wrist.stl: wrist.scad
	openscad -o 3dprint_parts/wrist.stl wrist.scad
	
clean:
	rm images/gello-ar4.png \
		3dprint_parts/ring.stl \
		3dprint_parts/l1.stl \
		3dprint_parts/arm1.stl \
		3dprint_parts/arm2.stl \
		3dprint_parts/wrist.stl \
