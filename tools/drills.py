"""Drills and coaching resources.

TO ADD A DRILL: find the right group below and add a line like this one.

    {"title": "Shell Drill, 4 on 4", "url": "https://youtu.be/XXXXXXXXXXX"},

That is the whole job. Rebuild and it appears on the page.

A YouTube link plays on the page when clicked. Anything else opens in a new
tab. Three optional extras:

    "note": "one line under the title"        a short description
    "see":  "zero-man-removed"                links to a knowledgebase entry
    "source": "Coach Wootten"                 credit, shown as a small tag

TO ADD A WHOLE GROUP: copy one of the ("slug", "Name", [...]) blocks.
Keep the slug lowercase with hyphens and unique.
"""

GROUPS = [
    ("drills-warmup", "Warm-Up and Fundamentals", [
        {"title": "Perfect Passing", "url": "https://www.youtube.com/watch?v=5xdS3vvPiWw",
         "note": "A warm-up that starts practice with the ball moving."},
        {"title": "Drill of the Week: Fundamental Work",
         "url": "https://www.youtube.com/watch?v=c18tNcyymLs"},
        {"title": "A Great Defensive Drill to Open Up Practice",
         "url": "https://www.youtube.com/watch?v=5CMTtMJX1CA"},
        {"title": "Drill video", "url": "https://youtu.be/yDePghRFQcE",
         "note": "Untitled in the resources list."},
    ]),

    ("drills-passing", "Passing", [
        {"title": "Pivot Passing", "url": "https://youtu.be/3eacbv3pcaw"},
        {"title": "82 Passes in 1 Minute", "url": "https://youtu.be/OituSPPT0q0"},
        {"title": "3-Person Pass, Cut and Replace",
         "url": "https://www.youtube.com/watch?v=8O0geioCEmM"},
        {"title": "Passing and Layups, 2 Minute Drill", "url": "https://youtu.be/Gsxfbk0_bsY"},
    ]),

    ("drills-shooting", "Shooting", [
        {"title": "UCLA Shooting Drill", "url": "https://www.youtube.com/watch?v=fCH-KH3PuOc"},
        {"title": "Jim Larranaga’s UCLA Drill, Shooting and Defense",
         "url": "https://www.youtube.com/watch?v=yxR0y-F2lF4"},
        {"title": "Cantafio’s Drill with Joe Wootten",
         "url": "https://fb.watch/n1XoviqxZU/?mibextid=YCRy0i", "source": "Facebook"},
    ]),

    ("drills-finishing", "Finishing and Layups", [
        {"title": "Play Off Two Feet", "url": "https://youtu.be/YzSXr6uNNVQ",
         "note": "Finishing on balance rather than off one foot."},
        {"title": "Layup Drills playlist",
         "url": "https://youtube.com/playlist?list=PLoMdDjCZ-6lLbtOoWDASaYhZEsBePaiyF"},
    ]),

    ("drills-defense", "Defense", [
        {"title": "The 7 Best Defense Drills for Basketball",
         "url": "https://youtu.be/mTkNmMqfTWs"},
        {"title": "The Lock Down Lane Slides Drill", "url": "https://youtu.be/XjtHczSvrUE"},
        {"title": "Butler Defense Drill",
         "url": "https://x.com/BreakthruBball/status/1700179706476147165", "source": "X"},
        {"title": "Suicide Defense Slides",
         "url": "https://x.com/LewisShine/status/1700108837896822861", "source": "X"},
        {"title": "Lane Slides",
         "url": "https://x.com/CoachShields_EC/status/1696493225962332490", "source": "X"},
        {"title": "Defensive drill post",
         "url": "https://x.com/hardwoodtexas/status/1701747635164680386", "source": "X",
         "note": "Untitled in the resources list."},
    ]),

    ("drills-rebounding", "Rebounding", [
        {"title": "Tubby Smith’s 2 on 1 Rebounding Drill",
         "url": "https://www.youtube.com/watch?v=dPtN8AJNk14"},
    ]),

    ("drills-transition", "Transition", [
        {"title": "Hoiberg’s Speed Drill",
         "url": "https://www.youtube.com/watch?v=3VT5-ewrRoM",
         "note": "Transition offense."},
        {"title": "3 Easy Transition Shooting Drills",
         "url": "https://www.youtube.com/watch?v=7rUWB3rOZu8"},
        {"title": "Russian Transition Shooting Drill",
         "url": "https://www.youtube.com/watch?v=UJkpATlvMjg"},
        {"title": "Greg McDermott’s 5 on 3 Drill for Transition Defense",
         "url": "https://youtu.be/_Jz6AfYN29c"},
        {"title": "BYU Transition Defense Drill", "url": "https://youtu.be/2sfelf23dk4"},
    ]),

    ("drills-offense", "Offense and Plays", [
        {"title": "3 Dribble Drive Motion Drills", "url": "https://youtu.be/XJHIQv59EGc"},
        {"title": "Early Practice Dribble Drive Motion Drills",
         "url": "https://coachtube.com/course_lesson/early-practice-dribble-drive-motion-basketball-drills/blood-22/13176869",
         "source": "CoachTube"},
        {"title": "The Basics of the Point Series, Princeton Offense",
         "url": "https://www.youtube.com/watch?v=YLYJJ7j_HZU", "see": "princeton-offense"},
        {"title": "Princeton Offense Point Series breakdown",
         "url": "https://www.hooperuniversity.com/breakdowns/princeton-offense-point-series",
         "source": "Hooper University", "see": "princeton-offense"},
        {"title": "Princeton Offense, Point Series, Over",
         "url": "http://www.fastmodelsports.com/library/basketball/fastdraw/352237/play-Princeton-Offense--Point-Series--Over",
         "source": "FastModel", "see": "princeton-offense"},
        {"title": "No More Set Plays: A Complete Guide to 5-Out Motion Offense",
         "url": "https://www.youtube.com/watch?v=ybns3yWMFYE", "see": "five-out-offense"},
    ]),

    ("drills-playlists", "Playlists", [
        {"title": "Drills playlist",
         "url": "https://www.youtube.com/playlist?list=PLUN_bpQCNSmueU6_aJpZhT8WcLf5t0Hj4"},
        {"title": "Drills playlist, second collection",
         "url": "https://www.youtube.com/playlist?list=PLvHGXD4hwKMcMJ5uCMUX4ynTaIjdEOhvu",
         "note": "Untitled in the resources list."},
    ]),

    ("drills-reading", "Further Reading", [
        {"title": "A guide to basketball cuts",
         "url": "https://www.basketballforcoaches.com/cutting/",
         "source": "Basketball For Coaches", "see": "cuts-list"},
        {"title": "Basketball cuts explained",
         "url": "https://www.thehoopsgeek.com/basketball-cuts/",
         "source": "The Hoops Geek", "see": "cuts-list"},
    ]),
]


# Written conditioning work. Edit the lines directly.
CONDITIONING = [
    ("Conditioning", "15 to 30 minutes", [
        "1 minute warm up",
        "30 second sprint on the treadmill or 1 sprint down and back",
        "30 second squat jumps",
        "45 seconds walking",
        "30 second sprint on the treadmill or 1 sprint down and back",
        "30 seconds horizon jumping over line or a cone",
        "45 seconds walking",
        "30 second sprint on the treadmill or 1 sprint down and back",
        "30 second lateral jumping",
        "30 seconds walking",
        "30 second sprint on the treadmill or 1 sprint down and back",
        "Jump rope 1 minute",
        "45 seconds walking",
        "30 seconds stationary lunges",
        "30 second sprint on the treadmill or 1 sprint down and back",
    ]),
    ("Sprint Work", "Build up over the week", [
        "Try to do 10 sprints for week then add more",
        "On treadmill play with incline and speed. If playing outside on a court then do full court layups.",
        "2 minutes warm up",
        "30 seconds sprinting",
        "1 minute walk",
    ]),
]
