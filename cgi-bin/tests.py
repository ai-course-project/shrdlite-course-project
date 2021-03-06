#!/usr/bin/env python3

import unittest
import interpreter
import PDDL
import simple_planner
import AStar.algorithm
import physics
import heuristic

class TestMain(unittest.TestCase):

    def setUp(self):
        self.stacks = [['floor0','a'],['floor1','b']]
        self.objects = {'a': {'size': 'large', 'form': 'ball', 'color': 'blue'},
                        'b': {'size': 'large', 'form': 'box', 'color': 'red'},
                        'floor0': {'color': None, 'form': 'floor', 'size': None},
                        'floor1': {'color': None, 'form': 'floor', 'size': None}}
        self.arm = 0
        self.holding = None
        self.costPick = 8
        self.costMove = 1
        self.intprt = [[('inside','a','b')]]
        self.state = (self.intprt,self.stacks,self.holding,self.arm,self.objects)

    def test_action(self):
        self.assertEqual(simple_planner.getAction(self.state),[('r',(self.intprt,self.stacks, self.holding, self.arm+1,self.objects),self.costMove),
                                                               ('p',(self.intprt,[['floor0'],['floor1','b']], 'a', self.arm ,self.objects),self.costPick),
                                                              ])

    def test_goal(self):
        self.assertFalse(simple_planner.goalWrapper(*self.state))

    def test_AStar(self):
        came_from, cost_so_far, actions_so_far, goal = AStar.algorithm.a_star_search(   simple_planner.getAction,
                                                            self.state,
                                                            simple_planner.goalWrapper,
                                                            heuristic.heuristic)
        (intprt, stacks, holding, arm, objects) = goal
        self.assertEqual(stacks,[['floor0'],['floor1','b','a']])

        self.assertEqual(
                        AStar.algorithm.getPlan(goal, came_from, actions_so_far,self.objects),
                        ['', AStar.algorithm.PICKING_UP + 'the ball','p','r',AStar.algorithm.DROP_IT,'d']
                        )


    def test_keyToObj(self):
        self.assertEqual(
                        AStar.algorithm.keyToObj( str(([['floor0'], ['floor1', 'b', 'a']], None, 1)), self.objects),
                        None
                        )
        self.assertEqual(
                        AStar.algorithm.keyToObj( str(([['floor0'], ['floor1', 'b']], 'a', 1)), self.objects),
                        {'size': 'large', 'form': 'ball', 'color': 'blue'}
                        )
        self.assertEqual(
                        AStar.algorithm.keyToObj( str(([['floor0'], ['floor1', 'b'],['floor1']], 'b', 1)), self.objects),
                        {'size': 'large', 'form': 'box', 'color': 'red'}
                        )




class TestAStar(unittest.TestCase):

    def setUp(self):
        self.stacks = [['floor0','a'],['floor1'],['floor2','b'],['floor3']]
        self.objects = {'a': {'size': 'large', 'form': 'ball', 'color': 'blue'},
                        'b': {'size': 'large', 'form': 'box', 'color': 'red'},
                        'floor0': {'color': None, 'form': 'floor', 'size': None},
                        'floor1': {'color': None, 'form': 'floor', 'size': None},
                        'floor2': {'color': None, 'form': 'floor', 'size': None},
                        'floor3': {'color': None, 'form': 'floor', 'size': None}}
        self.arm = 0
        self.holding = None
        self.intprt = [[('inside','a','b')]]
        self.state = (self.intprt,self.stacks,self.holding,self.arm,self.objects)

    def test_AStar(self):
        came_from, cost_so_far, actions_so_far, goal = AStar.algorithm.a_star_search(   simple_planner.getAction,
                                                            self.state,
                                                            simple_planner.goalWrapper,
                                                            heuristic.heuristic)
        (intprt, stacks, holding, arm, objects) = goal
        self.assertEqual(stacks,[['floor0'],['floor1'],['floor2','b','a'],['floor3']])
        self.assertEqual(AStar.algorithm.getPlan(goal, came_from, actions_so_far,self.objects), [AStar.algorithm.PICKING_UP + 'the large blue ball','p','r','r',AStar.algorithm.DROP_IT,'d'])

class TestActions(unittest.TestCase):

    def setUp(self):
        self.stacks = [['floor0','a'],['floor1']]
        self.objects = {'a': {'size': 'large', 'form': 'ball', 'color': 'blue'},
                        'b': {'size': 'large', 'form': 'box', 'color': 'red'},
                        'floor0': {'color': None, 'form': 'floor', 'size': None},
                        'floor1': {'color': None, 'form': 'floor', 'size': None}
                        }
        self.arm = 1
        self.holding = 'b'
        self.intprt = ('inside','a','b')
        self.state = (self.intprt,self.stacks,self.holding,self.arm,self.objects)

    def test_ungrasp(self):
        self.assertEqual(simple_planner._ungrasp(*self.state),
            (self.intprt, [['floor0','a'],['floor1','b']], None, 1, self.objects))

    def test_grasp(self):
        self.assertEqual(simple_planner._grasp(
             self.intprt,[['floor0','a'],['floor1','b']],None,0,self.objects),
            (self.intprt, [['floor0'],['floor1','b']], 'a', 0, self.objects))

    def test_grasp_two_obj(self):
        self.assertEqual(simple_planner._grasp(
            self.intprt, [['floor0','b'],['floor1']], 'a',0, self.objects),
            None)

    def test_grasp_floor(self):
        self.assertEqual(simple_planner._grasp(
            self.intprt, [['floor0','b','a'],['floor1']], None,1, self.objects),
            None)

    def test_left(self):
        self.assertEqual(simple_planner._left(*self.state),
            (self.intprt, [['floor0','a'],['floor1']], 'b', 0, self.objects))

    def test_left_None(self):
        self.assertEqual(simple_planner._left(
            self.intprt,[['floor0','a'],['floor1','b']],None,0,self.objects),
            None)

    def test_right_None(self):
        self.assertEqual(simple_planner._right(*self.state),
            None)

    def test_right_Move(self):
        self.assertEqual(simple_planner._right(
            self.intprt,self.stacks,'b',0,self.objects),
            (self.intprt,self.stacks,'b',1,self.objects))

class TestPhysics(unittest.TestCase):

    def setUp(self):
        self.stacks  = [[],[]]
        self.holding = None
        self.arm     = 0
        self.objects = {'lba': {'size': 'large', 'form': 'ball', 'color': 'blue'},
                        'sba': {'size': 'small', 'form': 'ball', 'color': 'red'},
                        'lbo': {'size': 'large', 'form': 'box', 'color': 'red'},
                        'sbo': {'size': 'small', 'form': 'box', 'color': 'red'},
                        'lbr': {'size': 'large', 'form': 'brick', 'color': 'red'},
                        'sbr': {'size': 'small', 'form': 'brick', 'color': 'red'},
                        'lpl': {'size': 'large', 'form': 'plank', 'color': 'red'},
                        'spl': {'size': 'small', 'form': 'plank', 'color': 'red'},
                        'lpy': {'size': 'large', 'form': 'pyramid', 'color': 'red'},
                        'spy': {'size': 'small', 'form': 'pyramid', 'color': 'red'},
                        'lta': {'size': 'large', 'form': 'table', 'color': 'red'},
                        'sta': {'size': 'small', 'form': 'table', 'color': 'red'},
                        'floor0': {'color': None, 'form': 'floor', 'size': None},
                        'floor1': {'color': None, 'form': 'floor', 'size': None},
                        'floor2': {'color': None, 'form': 'floor', 'size': None},
                        'floor3': {'color': None, 'form': 'floor', 'size': None},
                        'floor4': {'color': None, 'form': 'floor', 'size': None},
                        'floor5': {'color': None, 'form': 'floor', 'size': None},
                        'floor6': {'color': None, 'form': 'floor', 'size': None},
                        'floor7': {'color': None, 'form': 'floor', 'size': None},
                        'floor8': {'color': None, 'form': 'floor', 'size': None},
                        'floor9': {'color': None, 'form': 'floor', 'size': None},
                        }
        self.state = (self.stacks,self.holding,self.arm,self.objects)

        # Large boxes cannot be supported by large pyramids.
    def test_support_LargeBox(self):
        self.assertFalse(physics.check_physics(
                ('ontop','lbo','lpy'),self.objects
                ))

        # Small boxes cannot be supported by small bricks or pyramids.
    def test_support_smallBox_smallBrick(self):
        self.assertFalse(physics.check_physics(
                ('ontop','sbo','sbr'),self.objects
                ))
    def test_support_smallBox_smallPyramid(self):
        self.assertFalse(physics.check_physics(
                ('ontop','sbo','spy'),self.objects
                ))
    def test_support_smallBox_largePyramid(self):
        self.assertTrue(physics.check_physics(
                ('ontop','sbo','lpy'),self.objects
                ))

        # Boxes cannot contain pyramids, planks or boxes of the same size.
    def test_support_smallPyramid_smallBox(self):
        self.assertFalse(physics.check_physics(
                ('inside','spy','sbo'),self.objects
                ))

    def test_support_smallPlank_smallBox(self):
        self.assertFalse(physics.check_physics(
                ('inside','spl','sbo'),self.objects
                ))

    def test_support_smallBox_smallBox(self):
        self.assertFalse(physics.check_physics(
                ('inside','sbo','sbo'),self.objects
                ))

    def test_support_largePyramid_smallBox(self):
        self.assertFalse(physics.check_physics(
                ('inside','lpy','lbo'),self.objects
                ))

    def test_support_largePlank_smallBox(self):
        self.assertFalse(physics.check_physics(
                ('inside','lpl','lbo'),self.objects
                ))

    def test_support_largeBox_smallBox(self):
        self.assertFalse(physics.check_physics(
                ('inside','lbo','lbo'),self.objects
                ))

        # Small objects cannot support large objects.
    def test_support_Smallobjects_LargeObjects(self):
        #for all small objects
        for small,v in self.objects.items():
            if v.get('size') is 'small':

                #test all large objects
                for large,v2 in self.objects.items():
                    if v2.get('size') is 'large':
                        self.assertFalse(physics.check_physics(
                                        ('ontop',large,small),self.objects
                                        ))


        # Balls cannot support anything.
    def test_support_Ball_Anything(self):
        for ball,v in self.objects.items():
            if v.get('form') is 'ball':

                for anyObj in self.objects.keys():
                    self.assertFalse(physics.check_physics(
                                        ('ontop',anyObj,ball),self.objects
                                        ))

        # Balls must be in boxes or on the floor, otherwise they roll away.
    # def test_balls_on_floor_or_Box(self):
    #     for ball,v in self.objects.items():
    #         if v.get('form') is 'ball':

    #             for obj,v2 in self.objects.items():
    #                 if (v2.get('form') is 'floor' or v2.get('form') is 'box') and v2.get('size') is 'large' :
    #                     self.assertTrue(physics.check_physics(
    #                                     ('ontop',ball,obj),self.objects
    #                                     ))
    #                 else:
    #                     self.assertFalse(physics.check_physics(
    #                                     ('ontop',ball,obj),self.objects
    #                                     ))

class TestGoal(unittest.TestCase):

    def setUp(self):
        self.stacks = [[],['b','a']]
        self.objects = {'a': {'size': 'large', 'form': 'ball', 'color': 'blue'},
                        'b': {'size': 'large', 'form': 'box', 'color': 'red'},
                        'c': {'size': 'large', 'form': 'pyramid', 'color': 'green'}}
        self.arm = 0
        self.holding = None

        self.state = (self.stacks,self.holding,self.arm,self.objects)


        # Testing inside PDDL
    def test_inside_true(self):
        self.assertTrue(simple_planner.goalWrapper([[('inside','a','b')]],*self.state))

    def test_inside_false_holding(self):
        self.assertFalse(simple_planner.goalWrapper(
            [[('inside','a','b')]],[[],['b']],'a', 1, self.objects))

    def test_inside_false(self):
        self.assertFalse(simple_planner.goalWrapper([[('inside','b','a')]],*self.state))


        # Testing ontop PDDL
    def test_ontop_true(self):
        self.assertTrue(simple_planner.goalWrapper([[('ontop','a','b')]],*self.state))

    def test_ontop_false(self):
        self.assertFalse(simple_planner.goalWrapper([[('ontop','b','a')]],*self.state))


        # Testing holding PDDL
    def test_holding_true(self):
        self.assertTrue(simple_planner.goalWrapper([[('holding',None, None)]],*self.state))


        # Testing above PDDL
    def test_above_true(self):
        self.assertTrue(simple_planner.goalWrapper(
            [[('above','a','b')]],[[],[],['b','c','a']],None,0,self.objects))

    def test_above_false(self):
        self.assertFalse(simple_planner.goalWrapper(
            [[('above','a','b')]],[[],[],['a','c','b']],None,0,self.objects))


        # Testing under PDDL
    def test_under_true(self):
        self.assertTrue(simple_planner.goalWrapper(
            [[('under','a','b')]],[[],[],['a','c','b']],None,0,self.objects))

    def test_under_false(self):
        self.assertFalse(simple_planner.goalWrapper(
            [[('under','a','b')]],[[],[],['b','c','a']],None,0,self.objects))


        # Testing beside PDDL
    def test_beside_true_2Stacks(self):
        self.assertTrue(simple_planner.goalWrapper(
            [[('beside','a','b')]],[['a'],['b']],None,0,self.objects))

    def test_beside_true_2Stacks2(self):
        self.assertTrue(PDDL.satisfy_pred(
            ('beside','a','b'),[['a'],['b']],None))

    def test_beside_true_2stacks3(self):
        self.assertTrue(PDDL.satisfy_beside(
            'a', 'b', [['a'],['b']], None
            ))

    def test_beside_true(self):
        self.assertTrue(simple_planner.goalWrapper(
            [[('beside','a','c')]],[['a'],['c'],['b']],None,0,self.objects))

    def test_beside_true2(self):
        self.assertTrue(PDDL.satisfy_beside(
            'a','b',[[],['a'],['b'],[]], None))

    def test_beside_false(self):
        self.assertFalse(simple_planner.goalWrapper(
            [[('beside','a','b')]],[['a'],['c'],['b']],None,0,self.objects))

    def test_beside_notFound(self):
        self.assertFalse(simple_planner.goalWrapper(
            [[('beside','a','b')]],[['a'],['c'],[]],'b',0,self.objects))


        # Testing leftof PDDL
    def test_leftof_true(self):
        self.assertTrue(simple_planner.goalWrapper(
            [[('leftof','a','b')]],[['a'],['c'],['b']],None,0,self.objects))

    def test_leftof_false(self):
        self.assertFalse(simple_planner.goalWrapper(
            [[('leftof','c','a')]],[['a'],[],['b']],'c',0,self.objects))


        # Testing rightof PDDL
    def test_rightof_true(self):
        self.assertTrue(simple_planner.goalWrapper(
            [[('rightof','b','a')]],[['a'],['c'],['b']],None,0,self.objects))

    def test_rightof_false(self):
        self.assertFalse(simple_planner.goalWrapper(
            [[('rightof','a','b')]],[['a'],['c'],['b']],None,0,self.objects))

class TestHeuristic(unittest.TestCase):

    def setUp(self):
        self.stacks = [['floor0','a','b'],['floor1']]
        self.objects = {'a': {'size': 'large', 'form': 'brick', 'color': 'blue'},
                        'b': {'size': 'large', 'form': 'brick', 'color': 'red'},
                        'c': {'size': 'large', 'form': 'brick', 'color': 'red'},
                        'd': {'size': 'large', 'form': 'brick', 'color': 'red'},
                        'e': {'size': 'large', 'form': 'brick', 'color': 'red'},
                        'f': {'size': 'large', 'form': 'brick', 'color': 'red'},
                        'floor0': {'color': None, 'form': 'floor', 'size': None},
                        'floor1': {'color': None, 'form': 'floor', 'size': None}
                        }
        self.arm = 0
        self.holding = None
        self.intprt = [[('ontop','a','b')]]
        self.state = (self.intprt,self.stacks,self.holding,self.arm,self.objects)

    def test_heuristic_stackpenalty(self):
        self.assertEqual(heuristic.heuristic(*self.state),heuristic.PLACE_IN_STACK_PENALTY+heuristic.NOT_HOLDING_PENALTY)

    def test_heuristic_zeroholding(self):
        self.assertEqual(heuristic.heuristic(self.intprt, [['c','f','a'],['d','e','b']], self.holding, self.arm, self.objects),
            0+heuristic.NOT_HOLDING_PENALTY)

    def test_heuristic_beside(self):
        self.assertEqual(heuristic.heuristic([[('beside', 'a', 'b')]],[['a'], ['b','c','d']],
            self.holding, self.arm, self.objects),0)

    def test_heuristic_beside_bad(self):
        self.assertEqual(heuristic.heuristic([[('beside', 'a', 'b')]],[['a','e','f','g'], [], ['b','c','d']],
            self.holding, self.arm, self.objects), heuristic.PLACE_IN_STACK_PENALTY*2)

    # We assume the stackScore function to return zero if the arm is holding the object.
    def test_stackScore_zero(self):
        self.assertEqual(heuristic._stackScore('a', [[],[]]), 0)

    def test_stackScore_three(self):
        self.assertEqual(heuristic._stackScore('a', [['a','b','c','d'],[]]), 3*heuristic.PLACE_IN_STACK_PENALTY)

    def test_placeScore_twenty(self):
        self.assertEqual(heuristic._placeScore('b', [['b'],['a'],['c']], 'leftof'), heuristic.CLOSE_TO_EDGE_PENALTY)

    def test_placeScore_huge(self):
        self.assertEqual(heuristic._placeScore('b', [['c'],['a'],['b','d','e','f','g']], 'rightof'),
            heuristic.CLOSE_TO_EDGE_PENALTY+heuristic.PLACE_IN_STACK_PENALTY*4)

    def test_holdingTest(self):
        self.assertEqual(heuristic._holdingScore('a', 'a'), 0)


if __name__ == '__main__':
    unittest.main()
