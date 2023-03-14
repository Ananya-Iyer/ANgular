# ANgular

ANgular is a tool for taking multiple playblasts using different cameras in a scene file and compiling into a single playblast.
An artist can see different views of the same file using this tool.


## Installation

Keep the ANgularBrain & ANgularBody py files and the ffmpeg.exe file in the maya scripts folder.
Make sure you copy the ffmpeg folder and the prefs folder to your maya documents to avoid unnecessary errors.
(You'll find the ffmpeg & prefs folder in the link here: https://drive.google.com/drive/folders/1wtCBZAOrAMOcNAbzzMR1m72yRbXBcWqe?usp=share_link)

Run the following in maya script editor
	
import ANgularBody
reload(ANgularBody)
ANgularBody.main()


## Contributing

For changes, please open an issue first to discuss what you would like to change.