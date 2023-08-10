# Python video cropper
This project is a pygame powered video player, that is capable of allowing for the cropping of videos (re-saving a selected smaller portion of the video).

![demo](https://github.com/FlynnHillier/video-crop/blob/readme/readme/demo.gif)

## Setup
### dependencies
In your terminal, run: 
`pip install -r requirements.txt`

## usage

### import
To open a video ready for cropping. Initialise the VideoCropper class from VideoCropper.py. Where `video.mp4` is the path to your target input video.
```python
from VideoCropper import VideoCropper

cropper = VideoCropper("video.mp4")
cropper.start()
```

### crop
To crop the area selected within the area selection rectangle. Click the `Enter` key while the window is selected. This will begin writing the selected area to the filepath specified in the `out_file_path` argument supplied to VideoCropper on instantiation. Furthermore, if the `quit_on_crop` argument is set to True, once the file is written, the window will close and the event loop will cease.


### aspect ratio
Fixed crop output aspect-ratios are supported. This is useful if you wish to select a portion of video with a specific resolution. For example, say you had a `16:9` resolution video, but wished to select a portion of the video with a `9:16` video - this feature would allow you to do so.

```python
cropper = VideoCropper("video.mp4",crop_aspect_ratio=9/16)
```

![demo-aspect-ratio](https://github.com/FlynnHillier/video-crop/blob/readme/readme/usage_aspect_ratio.gif)

If instead an aspect ratio is not specified, the user is free to select any area - without maintaing a specific aspect ratio.

![demo-no-aspect-ratio](https://github.com/FlynnHillier/video-crop/blob/readme/readme/usage_no_aspect_ratio.gif)


## Future plans
This project was alot more hassle to develop than i expected when i initially started. I intended it to take a few days if that, however moulding my intentions around pygame's perhaps unsuitable (for my intentions) framework proved tricky and took longer than expected (about 3 weeks).

There are a few things i would like to add, however i doubt i will actually end up dedicating more time to this project as there are other projects i think my time would be better spent on.

- video trimming interface (on progress bar)
- button for toggling crop overlay (and trimming if added)
- in built file selection interface / pop-up
- thread process that crops video (prevent invoulantry freeze when clicking enter)