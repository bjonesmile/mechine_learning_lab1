"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    last_ball_pos = (-1, -1)
    first_crash = False
    second_crash = False
    bar_stay_L = False
    bar_stay_R = False

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        if last_ball_pos[0] == -1 :
            last_ball_pos = scene_info.ball
        ball_x = scene_info.ball[0]
        ball_y = scene_info.ball[1]
        platform_x = scene_info.platform[0]
        isDown = False
        isUp = False
        ball_move_R = False
        ball_move_L = False
        # define first time crash ti which side wall
        if last_ball_pos[1] - ball_y < 0 :
            isDown = True
        elif last_ball_pos[1] - ball_y > 0 :
            isUp = True
        
        if isDown and first_crash == False :
            
            if ball_x > 190 :
                first_crash = True
                bar_stay_R = True
            if ball_x < 10 :
                first_crash = True
                bar_stay_L = True
        elif isDown and first_crash :
            if second_crash == False :
                bar_stay_R = False
                bar_stay_L = False

            if ball_x > 190 :
                second_crash = True
                bar_stay_R = True
            if ball_x < 10 :
                second_crash = True
                bar_stay_L = True
        elif isUp :
            first_crash = False
            bar_stay_R = False
            bar_stay_L = False

        if isDown and 400 - ball_y <=80 :
            if ball_x + 2.5 > platform_x + 20 :
                ball_move_R = True
            elif ball_x + 2.5 < platform_x + 20 :
                ball_move_L = True
            else :
                pass
        elif isDown and ball_y > 300 :
            """
            if ball_x - last_ball_pos[0] > 0 and ball_x + 2.5 > platform_x + 20:
                ball_move_R = True
            elif ball_x - last_ball_pos[0] > 0 and ball_x + 2.5 < platform_x + 20:
                ball_move_L = True
            elif ball_x - last_ball_pos[0] < 0 and ball_x + 2.5 < platform_x + 20 :
                ball_move_R = True
            elif ball_x - last_ball_pos[0] < 0 and ball_x + 2.5 > platform_x + 20 :
                ball_move_L = True
            else :
                pass
            """
            
        elif isDown and first_crash :
            
            
            if bar_stay_R == True :
                if platform_x < 140 :
                    ball_move_R = True
                elif platform_x > 140 :
                    ball_move_L = True
                else :
                    ball_move_R = False
                    ball_move_L = False
            elif bar_stay_L == True :
                if platform_x < 20 :
                    ball_move_R = True
                elif platform_x > 20 :
                    ball_move_L = True
                else :
                    ball_move_R = False
                    ball_move_L = False
            else:
                pass
        if isUp :
            ball_move_R = False
            ball_move_L = False
            if platform_x + 20 > 100 :
                ball_move_L = True
            elif platform_x + 20 < 100 :
                ball_move_R = True
            else :
                pass
        else :
            pass
        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            
            if ball_move_R == True :
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif ball_move_L == True :
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else :
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            last_ball_pos = scene_info.ball
