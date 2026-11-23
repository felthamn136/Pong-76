        ORG     30000

START:  LD      SP, 65280
        XOR     A
        OUT     (254), A
        LD      A, 96
        LD      (LEFT_Y), A
        LD      (RIGHT_Y), A
        LD      (BALL_Y), A
        LD      A, 128
        LD      (BALL_X), A
        LD      A, 4
        LD      (BALL_VX), A
        LD      A, 2
        LD      (BALL_VY), A
        XOR     A
        LD      (LEFT_SCORE), A
        LD      (RIGHT_SCORE), A
        LD      (GAME_OVER), A
        LD      (BALL_TICK), A
        LD      (AI_TICK), A
        LD      (PADDLE_LARGE), A
        LD      (FAST_SPEED), A
        LD      (GREEN_COLOUR), A
        LD      A, 1
        LD      (MODE), A
        LD      (WAITING), A
        CALL    SHOW_MENU
        CALL    APPLY_SETTINGS
        CALL    CLEAR_SCREEN
        CALL    DRAW_STATIC

MAIN_LOOP:
        HALT
        LD      A, (GAME_OVER)
        OR      A
        JP      NZ, RESTART_WAIT
        LD      A, (WAITING)
        OR      A
        JP      NZ, SERVE_WAIT
        CALL    DRAW_BALL
        LD      A, (LEFT_Y)
        LD      (OLD_LEFT_Y), A
        LD      A, (RIGHT_Y)
        LD      (OLD_RIGHT_Y), A
        CALL    MOVE_PADDLES
        CALL    UPDATE_PADDLES
        CALL    ADVANCE_BALL
        CALL    DRAW_BALL
        JP      MAIN_LOOP

SERVE_WAIT:
        CALL    SELECT_MODE
        CALL    SPACE_PRESSED
        JP      NZ, MAIN_LOOP
        XOR     A
        LD      (WAITING), A
        JP      MAIN_LOOP

RESTART_WAIT:
        CALL    SPACE_PRESSED
        JP      NZ, MAIN_LOOP
RESTART_RELEASE:
        HALT
        CALL    SPACE_PRESSED
        JR      Z, RESTART_RELEASE
        JP      START

SELECT_MODE:
        LD      BC, 63486
        IN      A, (C)
        BIT     0, A
        JR      Z, MODE_ONE
        BIT     1, A
        RET     NZ
        LD      A, 2
        LD      (MODE), A
        RET
MODE_ONE:
        LD      A, 1
        LD      (MODE), A
        RET

SHOW_MENU:
        LD      HL, MENU_SCREEN
        LD      DE, 16384
        LD      BC, 6912
        LDIR
        XOR     A
        LD      (MENU_NOTE), A
        LD      (MENU_TICK), A
MENU_LOOP:
        HALT
        CALL    SELECT_MODE
        CALL    SELECT_SETTINGS
        CALL    HIGHLIGHT_MENU
        CALL    SPACE_PRESSED
        JR      Z, MENU_RELEASE
        CALL    MENU_MUSIC
        JR      MENU_LOOP
MENU_RELEASE:
        HALT
        CALL    SPACE_PRESSED
        JR      Z, MENU_RELEASE
        RET

MENU_MUSIC:
        LD      A, (MENU_TICK)
        CP      3
        JR      Z, MENU_NEXT_NOTE
        LD      A, (MENU_NOTE)
        LD      L, A
        LD      H, 0
        LD      DE, MENU_MELODY
        ADD     HL, DE
        LD      A, (HL)
        OR      A
        JR      Z, MENU_MUSIC_ADVANCE
        LD      D, A
        LD      E, 8
        CALL    PLAY_TONE
MENU_MUSIC_ADVANCE:
        LD      A, (MENU_TICK)
        INC     A
        LD      (MENU_TICK), A
        RET
MENU_NEXT_NOTE:
        XOR     A
        LD      (MENU_TICK), A
        LD      A, (MENU_NOTE)
        INC     A
        AND     31
        LD      (MENU_NOTE), A
        RET

SELECT_SETTINGS:
        LD      BC, 63486
        IN      A, (C)
        LD      D, A
        BIT     2, D
        JR      NZ, SETTINGS_LARGE
        XOR     A
        LD      (PADDLE_LARGE), A
SETTINGS_LARGE:
        BIT     3, D
        JR      NZ, SETTINGS_SLOW
        LD      A, 1
        LD      (PADDLE_LARGE), A
SETTINGS_SLOW:
        BIT     4, D
        JR      NZ, SETTINGS_FAST
        XOR     A
        LD      (FAST_SPEED), A
SETTINGS_FAST:
        LD      BC, 61438
        IN      A, (C)
        LD      D, A
        BIT     4, D
        JR      NZ, SETTINGS_WHITE
        LD      A, 1
        LD      (FAST_SPEED), A
SETTINGS_WHITE:
        BIT     3, D
        JR      NZ, SETTINGS_GREEN
        XOR     A
        LD      (GREEN_COLOUR), A
SETTINGS_GREEN:
        BIT     2, D
        RET     NZ
        LD      A, 1
        LD      (GREEN_COLOUR), A
        RET

HIGHLIGHT_MENU:
        LD      A, (MODE)
        DEC     A
        LD      HL, 22946
        CALL    HIGHLIGHT_PAIR
        LD      A, (PADDLE_LARGE)
        LD      HL, 23010
        CALL    HIGHLIGHT_PAIR
        LD      A, (FAST_SPEED)
        LD      HL, 23074
        CALL    HIGHLIGHT_PAIR
        LD      A, (GREEN_COLOUR)
        LD      HL, 23138
        JP      HIGHLIGHT_PAIR

HIGHLIGHT_PAIR:
        OR      A
        LD      A, 70
        LD      B, 7
        JR      Z, HIGHLIGHT_FIRST_INIT
        LD      A, 7
        LD      B, 70
HIGHLIGHT_FIRST_INIT:
        LD      C, 14
HIGHLIGHT_FIRST:
        LD      (HL), A
        INC     HL
        DEC     C
        JR      NZ, HIGHLIGHT_FIRST
        INC     HL
        LD      A, B
        LD      C, 14
HIGHLIGHT_SECOND:
        LD      (HL), A
        INC     HL
        DEC     C
        JR      NZ, HIGHLIGHT_SECOND
        RET

APPLY_SETTINGS:
        LD      A, (PADDLE_LARGE)
        OR      A
        LD      A, 12
        JR      Z, APPLY_PADDLE
        LD      A, 18
APPLY_PADDLE:
        LD      (PADDLE_HALF), A
        LD      B, A
        ADD     A, 32
        LD      (PADDLE_MIN), A
        LD      A, 174
        SUB     B
        LD      (PADDLE_MAX), A
        RET

SPACE_PRESSED:
        LD      BC, 32766
        IN      A, (C)
        BIT     0, A
        RET

MOVE_PADDLES:
        LD      BC, 65022
        IN      A, (C)
        BIT     0, A
        JR      NZ, LEFT_DOWN
        LD      A, (PADDLE_MIN)
        ADD     A, 4
        LD      B, A
        LD      A, (LEFT_Y)
        CP      B
        JR      NC, LEFT_UP_STEP
        LD      A, B
LEFT_UP_STEP:
        SUB     4
        LD      (LEFT_Y), A
LEFT_DOWN:
        LD      BC, 65278
        IN      A, (C)
        BIT     1, A
        JR      NZ, RIGHT_CONTROL
        LD      A, (PADDLE_MAX)
        SUB     4
        LD      B, A
        LD      A, (LEFT_Y)
        CP      B
        JR      C, LEFT_DOWN_STEP
        LD      A, B
LEFT_DOWN_STEP:
        ADD     A, 4
        LD      (LEFT_Y), A

RIGHT_CONTROL:
        LD      A, (MODE)
        CP      2
        JP      Z, PLAYER_TWO
        LD      A, (AI_TICK)
        INC     A
        CP      3
        JR      C, AI_REACT
        XOR     A
        LD      (AI_TICK), A
        RET
AI_REACT:
        LD      (AI_TICK), A
        LD      A, (BALL_VX)
        OR      A
        JP      M, AI_CENTER
        LD      A, (BALL_Y)
        LD      B, A
        LD      A, (PADDLE_MIN)
        CP      B
        JR      C, AI_MAX
        LD      B, A
AI_MAX: LD      A, (PADDLE_MAX)
        CP      B
        JR      NC, AI_TARGET_READY
        LD      B, A
AI_TARGET_READY:
        LD      A, B
        JR      AI_MOVE
AI_CENTER:
        LD      A, 96
AI_MOVE:
        LD      B, A
        LD      A, (RIGHT_Y)
        CP      B
        RET     Z
        JR      C, AI_DOWN
        SUB     B
        CP      2
        JR      C, AI_SET_TARGET
        LD      A, (RIGHT_Y)
        SUB     2
        LD      (RIGHT_Y), A
        RET
AI_DOWN:
        LD      A, B
        LD      C, A
        LD      A, (RIGHT_Y)
        LD      B, A
        LD      A, C
        SUB     B
        CP      2
        JR      C, AI_SET_DOWN_TARGET
        LD      A, B
        ADD     A, 2
        LD      (RIGHT_Y), A
        RET
AI_SET_DOWN_TARGET:
        LD      A, C
        LD      (RIGHT_Y), A
        RET
AI_SET_TARGET:
        LD      A, B
        LD      (RIGHT_Y), A
        RET

PLAYER_TWO:
        LD      BC, 57342
        IN      A, (C)
        BIT     1, A
        JR      NZ, P2_DOWN
        LD      A, (PADDLE_MIN)
        ADD     A, 4
        LD      B, A
        LD      A, (RIGHT_Y)
        CP      B
        JR      NC, P2_UP_STEP
        LD      A, B
P2_UP_STEP:
        SUB     4
        LD      (RIGHT_Y), A
P2_DOWN:
        LD      BC, 49150
        IN      A, (C)
        BIT     1, A
        RET     NZ
        LD      A, (PADDLE_MAX)
        SUB     4
        LD      B, A
        LD      A, (RIGHT_Y)
        CP      B
        JR      C, P2_DOWN_STEP
        LD      A, B
P2_DOWN_STEP:
        ADD     A, 4
        LD      (RIGHT_Y), A
        RET

ADVANCE_BALL:
        LD      A, (FAST_SPEED)
        OR      A
        JP      NZ, MOVE_BALL
        LD      A, (BALL_TICK)
        INC     A
        CP      6
        JR      C, ADVANCE_MOVE
        XOR     A
        LD      (BALL_TICK), A
        RET
ADVANCE_MOVE:
        LD      (BALL_TICK), A
        JP      MOVE_BALL

MOVE_BALL:
        LD      A, (BALL_X)
        LD      B, A
        LD      A, (BALL_VX)
        ADD     A, B
        LD      (BALL_X), A
        LD      A, (BALL_Y)
        LD      B, A
        LD      A, (BALL_VY)
        ADD     A, B
        LD      (BALL_Y), A

        LD      A, (BALL_Y)
        CP      32
        JR      NC, CHECK_BOTTOM
        LD      A, 32
        LD      (BALL_Y), A
        LD      A, (BALL_VY)
        NEG
        LD      (BALL_VY), A
        CALL    BEEP_WALL
        JR      CHECK_PADDLE
CHECK_BOTTOM:
        CP      172
        JR      C, CHECK_PADDLE
        LD      A, 172
        LD      (BALL_Y), A
        LD      A, (BALL_VY)
        NEG
        LD      (BALL_VY), A
        CALL    BEEP_WALL

CHECK_PADDLE:
        LD      A, (BALL_VX)
        OR      A
        JP      M, CHECK_LEFT_PADDLE

        LD      A, (BALL_X)
        CP      227
        JR      C, MOVE_DONE
        CP      231
        JR      NC, MISS_RIGHT
        LD      A, (RIGHT_Y)
        LD      B, A
        LD      A, (BALL_Y)
        SUB     B
        CALL    BALL_INTERSECTS_PADDLE
        JR      NC, MISS_RIGHT
        LD      A, 226
        LD      (BALL_X), A
        LD      A, (BALL_VX)
        NEG
        LD      (BALL_VX), A
        CALL    BEEP_PADDLE
        RET
MISS_RIGHT:
        LD      A, (BALL_X)
        CP      250
        JR      C, MOVE_DONE
        JP      SCORE_LEFT

CHECK_LEFT_PADDLE:
        LD      A, (BALL_X)
        CP      29
        JR      NC, MOVE_DONE
        CP      25
        JR      C, MISS_LEFT
        LD      A, (LEFT_Y)
        LD      B, A
        LD      A, (BALL_Y)
        SUB     B
        CALL    BALL_INTERSECTS_PADDLE
        JR      NC, MISS_LEFT
        LD      A, 29
        LD      (BALL_X), A
        LD      A, (BALL_VX)
        NEG
        LD      (BALL_VX), A
        CALL    BEEP_PADDLE
        RET
MISS_LEFT:
        LD      A, (BALL_X)
        CP      6
        RET     NC
        JP      SCORE_RIGHT

MOVE_DONE:
        RET

BALL_INTERSECTS_PADDLE:
        LD      B, A
        LD      A, (PADDLE_HALF)
        ADD     A, 2
        ADD     A, B
        LD      C, A
        LD      A, (PADDLE_HALF)
        ADD     A, A
        ADD     A, 3
        LD      B, A
        LD      A, C
        CP      B
        RET

BEEP_WALL:
        LD      A, 200
        JR      BEEP_TONE
BEEP_PADDLE:
        LD      A, 110
BEEP_TONE:
        PUSH    AF
        PUSH    BC
        PUSH    DE
        LD      D, A
        LD      E, 6
        CALL    PLAY_TONE
        POP     DE
        POP     BC
        POP     AF
        RET
PLAY_TONE:
BEEP_LOOP:
        LD      A, 16
        OUT     (254), A
        LD      B, D
BEEP_HIGH_DELAY:
        DJNZ    BEEP_HIGH_DELAY
        XOR     A
        OUT     (254), A
        LD      B, D
BEEP_LOW_DELAY:
        DJNZ    BEEP_LOW_DELAY
        DEC     E
        JR      NZ, BEEP_LOOP
        RET

SCORE_LEFT:
        LD      A, (LEFT_SCORE)
        INC     A
        LD      (LEFT_SCORE), A
        CALL    DRAW_SCORES
        CALL    CHECK_LEFT_WIN
        LD      A, 128
        LD      (BALL_X), A
        LD      A, 96
        LD      (BALL_Y), A
        LD      A, 252
        LD      (BALL_VX), A
        LD      A, 1
        LD      (WAITING), A
        RET

SCORE_RIGHT:
        LD      A, (RIGHT_SCORE)
        INC     A
        LD      (RIGHT_SCORE), A
        CALL    DRAW_SCORES
        CALL    CHECK_RIGHT_WIN
        LD      A, 128
        LD      (BALL_X), A
        LD      A, 96
        LD      (BALL_Y), A
        LD      A, 4
        LD      (BALL_VX), A
        LD      A, 1
        LD      (WAITING), A
        RET

CHECK_LEFT_WIN:
        LD      A, (LEFT_SCORE)
        CP      11
        RET     C
        LD      B, A
        LD      A, (RIGHT_SCORE)
        LD      C, A
        LD      A, B
        SUB     C
        RET     C
        CP      2
        RET     C
        LD      A, 1
        LD      (GAME_OVER), A
        LD      A, 4
        OUT     (254), A
        LD      HL, PLAYER_ONE_WINS
        CALL    DRAW_WINNER
        RET

CHECK_RIGHT_WIN:
        LD      A, (RIGHT_SCORE)
        CP      11
        RET     C
        LD      B, A
        LD      A, (LEFT_SCORE)
        LD      C, A
        LD      A, B
        SUB     C
        RET     C
        CP      2
        RET     C
        LD      A, 1
        LD      (GAME_OVER), A
        LD      A, 2
        OUT     (254), A
        LD      A, (MODE)
        CP      2
        LD      HL, PLAYER_TWO_WINS
        JR      Z, RIGHT_WINNER_READY
        LD      HL, COMPUTER_WINS
RIGHT_WINNER_READY:
        CALL    DRAW_WINNER
        RET

DRAW_WINNER:
        LD      A, 64
        CALL    DRAW_WIN_TEXT
        LD      HL, WINNER_PROMPT
        LD      A, 160
DRAW_WIN_TEXT:
        LD      (WINNER_ROW_OFFSET), A
        LD      C, 9
WINNER_CHARACTER:
        LD      A, (HL)
        OR      A
        RET     Z
        PUSH    HL
        LD      L, A
        LD      H, 0
        ADD     HL, HL
        ADD     HL, HL
        ADD     HL, HL
        LD      DE, (23606)
        ADD     HL, DE
        LD      D, 72
        LD      A, (WINNER_ROW_OFFSET)
        ADD     A, C
        LD      E, A
        LD      B, 8
WINNER_ROW:
        LD      A, (HL)
        LD      (DE), A
        INC     HL
        INC     D
        DJNZ    WINNER_ROW
        POP     HL
        INC     HL
        INC     C
        JR      WINNER_CHARACTER

DRAW_STATIC:
        CALL    DRAW_WALLS
        CALL    DRAW_CENTER_LINE
        CALL    DRAW_SCORES
        CALL    DRAW_MOVING
        RET

DRAW_CENTER_LINE:
        LD      B, 36
        LD      C, 128
CENTER_DASH:
        CALL    PLOT_POINT
        INC     B
        CALL    PLOT_POINT
        LD      A, B
        ADD     A, 7
        LD      B, A
        CP      170
        JR      C, CENTER_DASH
        RET

DRAW_SCORES:
        LD      A, (LEFT_SCORE)
        LD      C, 8
        CALL    DRAW_SCORE
        LD      A, (RIGHT_SCORE)
        LD      C, 21
        JP      DRAW_SCORE

DRAW_SCORE:
        LD      B, 0
SCORE_HUNDREDS:
        CP      100
        JR      C, SCORE_TENS_INIT
        SUB     100
        INC     B
        JR      SCORE_HUNDREDS
SCORE_TENS_INIT:
        LD      D, 0
SCORE_TENS:
        CP      10
        JR      C, SCORE_DIGITS
        SUB     10
        INC     D
        JR      SCORE_TENS
SCORE_DIGITS:
        LD      E, A
        LD      A, B
        OR      A
        JR      NZ, SCORE_DRAW_HUNDREDS
        LD      A, 10
SCORE_DRAW_HUNDREDS:
        CALL    DRAW_DIGIT
        INC     C
        LD      A, B
        OR      D
        JR      NZ, SCORE_DRAW_TENS
        LD      A, 10
        JR      SCORE_TENS_READY
SCORE_DRAW_TENS:
        LD      A, D
SCORE_TENS_READY:
        CALL    DRAW_DIGIT
        INC     C
        LD      A, E
        JP      DRAW_DIGIT

DRAW_DIGIT:
        PUSH    BC
        PUSH    DE
        LD      L, A
        LD      H, 0
        ADD     HL, HL
        ADD     HL, HL
        ADD     HL, HL
        LD      DE, DIGIT_BITMAPS
        ADD     HL, DE
        EX      DE, HL
        LD      B, 4
DIGIT_ROW:
        LD      A, B
        AND     7
        OR      64
        LD      H, A
        LD      A, B
        AND     56
        RLCA
        RLCA
        OR      C
        LD      L, A
        LD      A, (DE)
        LD      (HL), A
        INC     H
        LD      (HL), A
        INC     DE
        INC     B
        INC     B
        LD      A, B
        CP      20
        JR      NZ, DIGIT_ROW
        POP     DE
        POP     BC
        RET

DRAW_MOVING:
        CALL    DRAW_LEFT_PADDLE
        CALL    DRAW_RIGHT_PADDLE
        CALL    DRAW_BALL
        RET

UPDATE_PADDLES:
        LD      A, (OLD_LEFT_Y)
        LD      B, A
        LD      A, (LEFT_Y)
        CP      B
        JR      Z, UPDATE_RIGHT
        PUSH    AF
        LD      A, B
        LD      (LEFT_Y), A
        CALL    DRAW_LEFT_PADDLE
        POP     AF
        LD      (LEFT_Y), A
        CALL    DRAW_LEFT_PADDLE
UPDATE_RIGHT:
        LD      A, (OLD_RIGHT_Y)
        LD      B, A
        LD      A, (RIGHT_Y)
        CP      B
        RET     Z
        PUSH    AF
        LD      A, B
        LD      (RIGHT_Y), A
        CALL    DRAW_RIGHT_PADDLE
        POP     AF
        LD      (RIGHT_Y), A
        JP      DRAW_RIGHT_PADDLE

CLEAR_SCREEN:
        LD      HL, 16384
        LD      (HL), 0
        LD      DE, 16385
        LD      BC, 6143
        LDIR
        LD      HL, 22528
        LD      A, (GREEN_COLOUR)
        OR      A
        LD      A, 71
        JR      Z, CLEAR_ATTRIBUTES
        LD      A, 68
CLEAR_ATTRIBUTES:
        LD      (HL), A
        LD      DE, 22529
        LD      BC, 767
        LDIR
        RET

DRAW_WALLS:
        LD      B, 24
        LD      C, 16
WALL_TOP:
        CALL    PLOT_POINT
        LD      A, C
        ADD     A, 4
        LD      C, A
        CP      240
        JR      C, WALL_TOP
        LD      B, 175
        LD      C, 16
WALL_BOTTOM:
        CALL    PLOT_POINT
        LD      A, C
        ADD     A, 4
        LD      C, A
        CP      240
        JR      C, WALL_BOTTOM
        RET

DRAW_LEFT_PADDLE:
        LD      A, (PADDLE_HALF)
        LD      B, A
        LD      A, (LEFT_Y)
        SUB     B
        LD      B, A
        LD      C, 3
        LD      E, 240
        JR      DRAW_PADDLE

DRAW_RIGHT_PADDLE:
        LD      A, (PADDLE_HALF)
        LD      B, A
        LD      A, (RIGHT_Y)
        SUB     B
        LD      B, A
        LD      C, 28
        LD      E, 7
DRAW_PADDLE:
        LD      A, (PADDLE_HALF)
        ADD     A, A
        LD      D, A
PADDLE_LOOP:
        LD      A, B
        AND     7
        OR      64
        LD      H, A
        LD      A, B
        AND     192
        RRCA
        RRCA
        RRCA
        OR      H
        LD      H, A
        LD      A, B
        AND     56
        RLCA
        RLCA
        OR      C
        LD      L, A
        LD      A, (HL)
        XOR     E
        LD      (HL), A
        LD      A, C
        CP      28
        JR      NZ, PADDLE_NEXT
        INC     HL
        LD      A, (HL)
        XOR     128
        LD      (HL), A
PADDLE_NEXT:
        INC     B
        DEC     D
        JR      NZ, PADDLE_LOOP
        RET

DRAW_BALL:
        PUSH    DE
        LD      A, (BALL_X)
        DEC     A
        LD      C, A
        AND     7
        LD      B, A
        LD      DE, 61440
        OR      A
        JR      Z, BALL_MASK_READY
BALL_MASK_SHIFT:
        SRL     D
        RR      E
        DJNZ    BALL_MASK_SHIFT
BALL_MASK_READY:
        LD      A, C
        SRL     A
        SRL     A
        SRL     A
        LD      C, A
        LD      A, (BALL_Y)
        DEC     A
        LD      B, A
        CALL    DRAW_BALL_ROW
        INC     B
        CALL    DRAW_BALL_ROW
        INC     B
        CALL    DRAW_BALL_ROW
        INC     B
        CALL    DRAW_BALL_ROW
        POP     DE
        RET

DRAW_BALL_ROW:
        LD      A, B
        AND     7
        OR      64
        LD      H, A
        LD      A, B
        AND     192
        RRCA
        RRCA
        RRCA
        OR      H
        LD      H, A
        LD      A, B
        AND     56
        RLCA
        RLCA
        OR      C
        LD      L, A
        LD      A, (HL)
        XOR     D
        LD      (HL), A
        LD      A, E
        OR      A
        RET     Z
        INC     HL
        LD      A, (HL)
        XOR     E
        LD      (HL), A
        RET

PLOT_POINT:
        PUSH    BC
        PUSH    DE
        LD      A, B
        AND     7
        OR      64
        LD      H, A
        LD      A, B
        AND     192
        RRCA
        RRCA
        RRCA
        OR      H
        LD      H, A

        LD      A, B
        AND     56
        RLCA
        RLCA
        LD      D, A
        LD      A, C
        SRL     A
        SRL     A
        SRL     A
        OR      D
        LD      L, A

        LD      A, C
        AND     7
        LD      E, A
        LD      A, E
        OR      A
        LD      A, 128
        JR      Z, PLOT_MASK_READY
PLOT_MASK_LOOP:
        SRL     A
        DEC     E
        JR      NZ, PLOT_MASK_LOOP
PLOT_MASK_READY:
        LD      E, A
        LD      A, (HL)
        XOR     E
        LD      (HL), A
        POP     DE
        POP     BC
        RET

LEFT_Y:       DB 96
RIGHT_Y:      DB 96
BALL_X:       DB 128
BALL_Y:       DB 96
BALL_VX:      DB 4
BALL_VY:      DB 2
BALL_TICK:    DB 0
AI_TICK:      DB 0
PADDLE_LARGE: DB 0
FAST_SPEED:   DB 0
GREEN_COLOUR: DB 0
PADDLE_HALF:  DB 12
PADDLE_MIN:   DB 44
PADDLE_MAX:   DB 162
OLD_LEFT_Y:   DB 96
OLD_RIGHT_Y:  DB 96
LEFT_SCORE:   DB 0
RIGHT_SCORE:  DB 0
MODE:         DB 1
WAITING:      DB 1
GAME_OVER:    DB 0
MENU_NOTE:    DB 0
MENU_TICK:    DB 0
WINNER_ROW_OFFSET: DB 0

MENU_MELODY:
        DB 255, 214, 170, 214, 190, 159, 127, 159
        DB 142, 170, 214, 170, 190, 214, 255, 0
        DB 214, 170, 127, 106, 112, 142, 170, 142
        DB 159, 190, 214, 159, 170, 134, 170, 0

PLAYER_ONE_WINS: DB "PLAYER 1 WINS", 0
PLAYER_TWO_WINS: DB "PLAYER 2 WINS", 0
COMPUTER_WINS:   DB "COMPUTER WINS", 0
WINNER_PROMPT:   DB "SPACE FOR MENU", 0

DIGIT_BITMAPS:
        DB  60, 102, 110, 118, 102, 102, 60, 0
        DB  24, 56, 24, 24, 24, 24, 126, 0
        DB  60, 102, 6, 12, 48, 96, 126, 0
        DB  60, 102, 6, 28, 6, 102, 60, 0
        DB  12, 28, 60, 108, 126, 12, 12, 0
        DB  126, 96, 124, 6, 6, 102, 60, 0
        DB  28, 48, 96, 124, 102, 102, 60, 0
        DB  126, 6, 12, 24, 48, 48, 48, 0
        DB  60, 102, 102, 60, 102, 102, 60, 0
        DB  60, 102, 102, 62, 6, 12, 56, 0
        DB  0, 0, 0, 0, 0, 0, 0, 0

MENU_SCREEN:
        INCBIN  "menu.scr"

        END
