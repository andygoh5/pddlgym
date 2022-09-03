(define (domain kitchen)
  (:requirements :strips :typing :disjunctive-preconditions)
  (:types thing location direction)
  (:predicates
	(is-agent ?v0 - thing)
	(is-object ?v0 - thing)
	(is-board ?v0 - location)
	(is-stove ?v0 - location)
	(is-counter ?v0 - location)

	(handsfree ?agent - thing)			; see if agent can pick up an object
	(holding ?agent - thing ?object - thing)
	(chopped ?object - thing)
	(cooked ?object - thing)
	(at ?v0 - thing ?v1 - location)
	(adjacent ?v0 - location ?v1 - location)

	; free parameter predicates
    (move ?v0 - direction)
    (pick ?arg0 - thing)
	(place ?object - thing ?object_loc - location)
	(chop ?object - thing)
	(cook ?object - thing)

	(clear ?v0 - location)
	(move-dir ?v0 - location ?v1 - location ?v2 - direction)

	(is-goal ?v0 - location)
	(is-nongoal ?v0 - location)
	(at-goal ?v0 - thing)
  )

  ; (:actions move pick place chop cook)

	(:action move
		:parameters (?a - thing ?from - location ?to - location ?dir - direction)
		:precondition (and (move ?dir)
			(is-agent ?a)
			(at ?a ?from)
			(clear ?to)
			(move-dir ?from ?to ?dir))
		:effect (and
			(not (at ?a ?from))
			(not (clear ?to))
			(at ?a ?to)
			(clear ?from))
	)

	(:action pick
		:parameters (?a - thing ?al - location ?o - thing ?ol - location)
		:precondition (and
            (pick ?o)
			(is-agent ?a)
			(is-object ?o)
			(handsfree ?a)
			(at ?a ?al)
			(at ?o ?ol)
			(adjacent ?al ?ol)
			)
		:effect (and
			(not (handsfree ?a))
			(holding ?a ?o)
			(not (at ?o ?ol)))
	)

	(:action place
		:parameters (?a - thing ?al - location ?o - thing ?ol - location)
		:precondition (and 
			(place ?o ?ol)
			(is-agent ?a)
			(is-object ?o)
			(at ?a ?al)
			(holding ?a ?o)
			(adjacent ?al ?ol)
			(not (clear ?ol))
		)
		:effect (and 
			(handsfree ?a)
			(at ?o ?ol)
			(not (holding ?a ?o))
		)
	)

	(:action chop
		:parameters (?agent - thing ?agent_loc - location ?object - thing ?object_loc - location)
		:precondition (and 
			(chop ?object)
			(is-agent ?agent)
			(is-object ?object)
			(at ?agent ?agent_loc)
			(at ?object ?object_loc)
			(is-board ?object_loc)
			(adjacent ?agent_loc ?object_loc)
		)
		:effect (and 
			(chopped ?object)
		)
	)

	(:action cook
		:parameters (?agent - thing ?agent_loc - location ?object - thing ?object_loc -location)
		:precondition (and 
			(cook ?object)
			(is-agent ?agent)
			(is-object ?object)
			(at ?agent ?agent_loc)
			(at ?object ?object_loc)
			(is-stove ?object_loc)
			(adjacent ?agent_loc ?object_loc)
			(chopped ?object)
		)
		:effect (and 
			(cooked ?object)
		)
	)
)