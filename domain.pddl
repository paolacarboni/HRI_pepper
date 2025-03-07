(define (domain care_center)
    (:requirements :strips :adl)

    (:types 
        care_giver  elder  robot   location 
    )

    (:predicates
        (is_elder_room ?e  - elder   ?loc  - location) 
        (is_elder_at ?e - elder ?loc - location)
        (is_care_giver_at   ?cg - care_giver    ?loc    - location)
        (is_robot_at  ?r - robot ?loc - location)
        (is_confused   ?e)
        (is_unsafe_loc   ?loc)
        (is_adj ?loc - location ?loc - location)
        (is_with_cg ?e - elder)
        (is_interacting ?r - robot ?e - elder)
    
    )


    (:action move
        :parameters (?r - robot ?from - location  ?to - location)

        :precondition (and  
                    (is_adj ?from ?to)
                    (is_robot_at ?r ?from)
        )

        :effect (and
                (not(is_robot_at ?r ?from))
                (is_robot_at ?r ?to)
        )
    )




    (:action move_elder
        :parameters (?r - robot  ?e -elder ?from - location  ?to - location)

        :precondition (and  
                    (is_robot_at ?r ?from)
                    (is_elder_at ?e ?from)
                    (is_adj ?from ?to)
                    (is_interacting ?r ?e)
                    
        )

        :effect (and
                (not(is_robot_at ?r ?from))
                (is_robot_at ?r ?to)
                (not(is_elder_at ?e ?from))
                (is_elder_at ?e ?to)
        )
    )




    (:action interact

        :parameters (?r -robot ?e - elder   ?loc -  location)

        :precondition (and 
                        (is_robot_at ?r ?loc)
                        (is_elder_at ?e ?loc)
                        (or  (is_confused ?e)
                            (is_unsafe_loc ?loc)
                        )
                       
                        (not(is_with_cg ?e))
                        (not(is_interacting ?r ?e))
        )
    
        :effect (and
                (is_interacting ?r ?e)
        )
    )


    


)