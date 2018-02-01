import pdb
import math


#Madrid
"""
40.478684,-3.807941
40.477640,-3.546329


40.331759,-3.818927
40.335161,-3.541522

"""
def main():
	
	#Barcelona
	x_one, y_one = 41.469673, 2.068600
	x_two, y_two = 41.469046, 2.228762
	x_three, y_three = 41.324677, 2.067055	
	x_four, y_four = 41.322872, 2.151170
	x = 41.3851
	y = 2.1734
	#Madrid
	#~ x_one, y_one = 40.572110, -3.887248
	#~ x_two, y_two = 40.575240, -3.357158
	#~ x_three, y_three = 40.289347,-3.909907
	#~ x_four, y_four = 40.278871,-3.367458
	x,y = int(sys.argv[1]), int(sys.argv[2])
	city = sys.argv[3]
	filename = 'new_tower_loc_no_mappings_removed.txt'
	out = open('towers_in_' + str(city) + '.csv', 'w')
	out.write('Latitude' + ',' + 'Longitude' + ',' + '\n')
	k = 0

	with open(filename, 'r') as f:
		
		for line in f:
			k+= 1
			line = line.strip().split(' ')
			
			tower_id = line[0]
			tower_lat = float(line[1])
			tower_long = float(line[2])
			
			new_row = line[0] + ',' 
			
			dist = math.sqrt((x - tower_lat)**2 + (y - tower_long)**2)
			if(dist < 0.07):
				
				print dist, tower_lat, tower_long
				out.write(str(tower_lat) + ',' + str(tower_long) + '\n')
				
	
	out.close()
	
if __name__ == "__main__":
	main()
