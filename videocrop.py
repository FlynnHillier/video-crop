import pygame
import cv2

def main():
    play_video("sample.mp4")


def play_video(fp:str):
    video = cv2.VideoCapture(fp)
    fps = video.get(cv2.CAP_PROP_FPS)
    success, frame = video.read()

    window = pygame.display.set_mode(frame.shape[1::-1],pygame.RESIZABLE)
    clock = pygame.time.Clock()

    paused = False

    run = success
    while run:
        clock.tick(fps)
        
        #handle events
        for event in pygame.event.get():
            match event.type:
                #handle user quit window
                case pygame.QUIT:
                    run = False
                
                #handle resize
                case pygame.VIDEORESIZE:
                    window = pygame.display.set_mode((event.w,event.h),pygame.RESIZABLE) #resize display
                    
                    frame = cv2.resize(frame,window.get_size()) #resize displayed frame (compress this into a function as is shared code to every frame update)
                    video_surf = pygame.image.frombuffer(frame.tobytes(),frame.shape[1::-1],"BGR")
                    window.blit(video_surf,(0,0))
                    pygame.display.flip()

                #handle keypress
                case pygame.KEYDOWN:

                    #quit on escape key press (for dev testing purposes)
                    if event.key == pygame.K_ESCAPE:
                        run = False
                    
                    #toggle pause video
                    if event.key == pygame.K_SPACE:
                        paused = not paused

                

        if not paused:
            #read next frame
            success,frame = video.read()

            if success:
                #resize frame to fit display
                frame = cv2.resize(frame,window.get_size())

                video_surf = pygame.image.frombuffer(
                    frame.tobytes(),frame.shape[1::-1],"BGR"
                )
            else:
                #no more frames left to read.
                run = False
            
            #write frame to window
            window.blit(video_surf,(0,0))
            pygame.display.flip()



if __name__ == "__main__":
    main()