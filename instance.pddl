(define (problem instance1)
    (:domain care_center)

(:objects
    c1      c2             - care_giver
    alessio beatrice carlotta  - elder  
    room_A  room_B  room_C  common_room  corridor  garden  exit - location
    pepper - robot
)

(:init 

(is_elder_room alessio room_A)
(is_elder_room beatrice room_B)
(is_elder_room carlotta room_C)
(is_robot_at pepper room_A)
(is_elder_at alessio corridor)
(is_elder_at beatrice common_room)
(is_elder_at carlotta exit)
(is_care_giver_at c1 corridor)
(is_care_giver_at c2 garden)
(is_with_cg alessio)
(is_confused beatrice)


(is_adj room_A corridor)
(is_adj corridor room_A)

(is_adj room_B corridor)
(is_adj corridor room_B)

(is_adj room_C corridor)
(is_adj corridor room_C)

(is_adj common_room corridor)
(is_adj corridor common_room)


(is_adj garden common_room)
(is_adj common_room garden)

(is_adj exit garden)
(is_adj garden exit)

(is_unsafe_loc exit)

)


(:goal (and

(is_robot_at pepper garden)
(is_elder_at carlotta room_C)
(is_elder_at beatrice room_B)


)


)


)