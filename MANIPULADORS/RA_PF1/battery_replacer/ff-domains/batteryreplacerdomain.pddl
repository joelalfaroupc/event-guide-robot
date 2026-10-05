(define (domain batteryreplacer)

(:requirements :strips :typing :conditional-effects :disjunctive-preconditions)

(:types obstacle robot location)

(:predicates
   (handEmpty ?rob - robot)
   (holding ?rob - robot ?obs - obstacle)
   (in ?obs - obstacle ?loc - location)
   (clear ?loc - location)        ;; True if a square is empty
   (is-graveyard ?loc - location) ;; Flags which location is the graveyard
   (consumed ?obs - obstacle)
)

(:action pick
   :parameters (?rob - robot ?obs - obstacle ?from - location)
   :precondition (and (handEmpty ?rob)
                      (in ?obs ?from))
   :effect (and (holding ?rob ?obs)
                (not (handEmpty ?rob))
                (not (in ?obs ?from))
                (clear ?from)) ;; Lifting a piece automatically empties the square
)

(:action place
   :parameters (?rob - robot ?obs - obstacle ?to - location)
   :precondition (and (holding ?rob ?obs)
                      ;; Conditional routing based on whether the obstacle is consumed
                      (or (and (consumed ?obs) (is-graveyard ?to))
                          (and (not (consumed ?obs)) (clear ?to))))
   :effect (and (handEmpty ?rob)
                (in ?obs ?to)
                (not (holding ?rob ?obs))
                
                ;; If placed on a normal square, it is no longer clear
                (when (not (is-graveyard ?to)) 
                      (not (clear ?to)))
                
                ;; If placed in the graveyard, it is officially flagged as consumed
                (when (is-graveyard ?to) 
                      (consumed ?obs))
           )
)

)