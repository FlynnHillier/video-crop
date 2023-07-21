import pygame
import cv2

def main():
    play_video("sample.mp4")


def play_video(fp:str):
    video = cv2.VideoCapture(fp)
    fps = video.get(cv2.CAP_PROP_FPS)
    success, video_image = video.read()

    window = pygame.display.set_mode(video_image.shape[1::-1],pygame.RESIZABLE)
    clock = pygame.time.Clock()

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
                    copy = pygame.display.get_surface()
                    window = pygame.display.set_mode((event.w,event.h),pygame.RESIZABLE)
                
                #handle keypress
                case pygame.KEYDOWN:

                    #quit on escape key press (for dev testing purposes)
                    if event.key == pygame.K_ESCAPE:
                        run = False
                

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