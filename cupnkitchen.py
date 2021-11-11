#
# "Grab a cup from the kitchen"
#
# where:
#     - "A cup" is an undefined instance of Cup
#     - "The kitchen" is a known place with defined attributes

# 1. A declarative version of the plan is created. Relations provide additional
#    information about how the defined instances interact with themselves, and
#    they can be key to filling missing gaps in knowledge.
#
# NOTE: let's just pretend that `defined-kitchen` is a Kitchen instance with
#       its attributes already defined.
SRC = '''
{plan
    {objects
        [the-kitchen defined-kitchen]
        [the-cup     (new Cup)]}
    [relations
        (contains the-kitchen the-cup)]
    [steps
        {GRAB
            [active False]
            [what   the-cup]
            [pre    (reachable? the-cup)]
            [post   (holding?   the-cup)]}]}
'''

# 2. The full plan is constructed dynamically by examining all prerequisites.
#    With the help of a knowledge base and an adequate planner, suitable
#    intermediate steps can be generated to solve them.
#
#    In this case, the only way we the `reachable?` predicate can change is
#    by moving to another location (at least the only *reasonable* way).
SRC = '''
{plan
    {objects
        [the-kitchen defined-kitchen]
        [the-cup     (new Cup)]}
    [relations
        (contains the-kitchen the-cup)]
    [steps
        {GOTO
            [active False]
            [where  nil]
            [post   (reachable? the-cup)]}
        {GRAB
            [active False]
            [what   the-cup]
            [pre    (reachable? the-cup)]
            [post   (holding?   the-cup)]}]}
'''

# 3. Step 2 cannot start because `where` isn't defined. Remember: the robot
#    must GOTO somewhere where `the-cup` is reachable. The only problem is
#    that it doesn't know about such place! The cameras can't see it and the
#    graph G doesn't have any info about that object.
#
#    Here comes the knowledge base. Sure, the robot doesn't know the cup's
#    location, but it knows that the cup is inside the kitchen. Moving there
#    could help.
SRC = '''
{plan
    {objects
        [the-kitchen defined-kitchen]
        [the-cup     (new Cup)]}
    [relations
        (contains the-kitchen the-cup)]
    [steps
        {GOTO
            [active False]
            [where  nil]
            [post   (inside? the-kitchen)]}
        {GOTO
            [active False]
            [where  nil]
            [post   (reachable? the-cup)]}
        {GRAB
            [active False]
            [what   the-cup]
            [pre    (reachable? the-cup)]
            [post   (holding?   the-cup)]}]}
'''

# 4. Now we're facing a similar problem. Step 3 cannot continue because `where`
#    is undefined. But in this case the problem can be solved easily: any point
#    inside the kitchen's bounding area will, by definition, fulfill Step 3's
#    post-condition. So we can fill in the gap by choosing a random point
#    inside that area:
SRC = '''
{plan
    {objects
        [the-kitchen defined-kitchen]
        [the-cup     (new Cup)]}
    [relations
        (contains the-kitchen the-cup)]
    [steps
        {GOTO
            [active False]
            [where  random-point-inside-kitchen]
            [post   (inside? the-kitchen)]}
        {GOTO
            [active False]
            [where  nil]
            [post   (reachable? the-cup)]}
        {GRAB
            [active False]
            [what   the-cup]
            [pre    (reachable? the-cup)]
            [post   (holding?   the-cup)]}]}
'''

# 5. Finally we have a fully-defined step with all its pre-conditions
#    satisfied! We can start it now:
SRC = '''
{plan
    {objects
        [the-kitchen defined-kitchen]
        [the-cup     (new Cup)]}
    [relations
        (contains the-kitchen the-cup)]
    [steps
        {GOTO
            [active True]
            [where  random-point-inside-kitchen]
            [post   (inside? the-kitchen)]}
        {GOTO
            [active False]
            [where  nil]
            [post   (reachable? the-cup)]}
        {GRAB
            [active False]
            [what   the-cup]
            [pre    (reachable? the-cup)]
            [post   (holding?   the-cup)]}]}
'''

# 6. Once there, the robot will be left with the same plan we had right before
#    phase 3, but now it can be re-evaluated while being inside the kitchen.
#    Maybe one camera will see a suitable cup. Maybe a different step can be
#    planned once inside the kitchen (like LOOK_AROUND). Let's assume a cup has
#    been found by the robot's sensors and all its details have been fetched:
SRC = '''
{plan
    {objects
        [the-kitchen defined-kitchen]
        [the-cup     cup-found-by-sensors}
    [relations
        (contains the-kitchen the-cup)]
    [steps
        {GOTO
            [active False]
            [where  nil]
            [post   (reachable? the-cup)]}
        {GRAB
            [active False]
            [what   the-cup]
            [pre    (reachable? the-cup)]
            [post   (holding?   the-cup)]}]}
'''

# 7. Now the `where` attribute of our original GOTO step can be filled: the
#    position of the cup is defined, so any point at random at reach-distance
#    of the robot will fulfill that condition:
SRC = '''
{plan
    {objects
        [the-kitchen defined-kitchen]
        [the-cup     cup-found-by-sensors}
    [relations
        (contains the-kitchen the-cup)]
    [steps
        {GOTO
            [active False]
            [where  random-point-near-cup]
            [post   (reachable? the-cup)]}
        {GRAB
            [active False]
            [what   the-cup]
            [pre    (reachable? the-cup)]
            [post   (holding?   the-cup)]}]}
'''

# 8. Once again, the robot can navigate towards that point and once it's there
#    the plan it's left with our original declarative definition (but with all
#    pre-requisites fulfilled):
SRC = '''
{plan
    {objects
        [the-kitchen defined-kitchen]
        [the-cup     cup-found-by-sensors}
    [relations
        (contains the-kitchen the-cup)]
    [steps
        {GRAB
            [active False]
            [what   the-cup]
            [pre    (reachable? the-cup)]
            [post   (holding?   the-cup)]}]}
'''