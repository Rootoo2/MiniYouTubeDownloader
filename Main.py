import subprocess
import customtkinter
import pytube
from pathlib import Path

from threading import Thread
from moviepy.editor import VideoFileClip
from time import sleep

import os
import sys

customtkinter.set_appearance_mode(
    "System"
)  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(
    "blue"
)  # Themes: "blue" (standard), "green", "dark-blue"


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class App(customtkinter.CTk):
    downloads_path = str(Path.home() / "Downloads")

    initialSize = None

    def __init__(self):
        super().__init__()
        self.iconbitmap(resource_path("icon.ico"))
        # configure window
        self.title("YouTube Downloader")
        self.geometry(f"{400}x{200}")

        # create sidebar frame with widgets

        self.logo_label = customtkinter.CTkLabel(
            self,
            text="YouTube Downloader",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.status = None

        self.progressbar = customtkinter.CTkProgressBar(
            master=self,
        )
        self.DropDown = customtkinter.CTkComboBox(
            master=self, values=["MP4 (Video)", "MP3 (Audio Only)"]
        )
        self.URL_Input = customtkinter.CTkEntry(
            master=self, placeholder_text="YouTube Link"
        )
        self.DownloadButton = customtkinter.CTkButton(
            master=self,
            command=self.startDownload,
            text_color="white",
            text="Start Download",
            text_color_disabled="white",
        )

        self.creditsLabel = customtkinter.CTkLabel(
            self,
            text="Made and Designed by Ben Esposito",
            font=customtkinter.CTkFont(
                size=10,
            ),
        )
        self.initialPack()

        self.resizable(False, False)

    def progCheck(self, stream, datachunk, byteRemaining):
        if byteRemaining != None:
            if self.initialSize == None:
                self.initialSize = byteRemaining
                self.updateProgressBar(0)
            else:
                percentDone = int(
                    ((self.initialSize - byteRemaining) / self.initialSize) * 100
                )
                self.updateProgressBar(percentDone)

    def onComplete(self, stream, filePath):
        try:
            if self.initialSize != None:
                self.showStatus(f"Complete check downloads folder")
            self.initialSize = None
            self.SwitchButtonState(False)
            self.hideProgressBar()

            if os.path.exists(filePath):
                filePath = self.checkFileFormat(filePath=filePath)
                self.showStatus("Download Complete")
                subprocess.Popen(rf"explorer /select,{filePath}")
        except:
            pass

    def checkFileFormat(self, filePath):
        if self.getIfMP4():
            return filePath
        else:
            originalFile = filePath
            self.updateProgressBar(100)
            self.showStatus("Converting to MP3")
            video = VideoFileClip(filePath)
            OriginalBaseName = os.path.basename(filePath)
            NewbaseName = str(OriginalBaseName).replace("mp4", "mp3")
            filePath = str(filePath).replace(OriginalBaseName, NewbaseName)
            video.audio.write_audiofile(filePath)
            video.close()
            sleep(0.5)
            try:
                print(originalFile)

                os.remove(originalFile)
            except Exception as e:
                print(e)

            return filePath

    def getIfMP4(self):
        Mp4Choice = self.DropDown.get()
        if Mp4Choice == "MP4 (Video)":
            return True
        else:
            return False

    def downloadYouTubeVid(
        self,
        link: str,
    ):
        try:
            # https://www.youtube.com/watch?v=55XJ1ObZKaM
            download = pytube.YouTube(
                url=link,
                on_progress_callback=self.progCheck,
                on_complete_callback=self.onComplete,
                use_oauth=False,
                allow_oauth_cache=True,
            )
            self.showStatus("Download started")
        except:
            self.showStatus("Invalid link", green=False)
            self.SwitchButtonState(False)
            self.hideProgressBar()
            return

        b = download.streams.filter(file_extension="mp4")

        if b.first() != None:
            b.first().download(self.downloads_path)
        else:
            self.showStatus(f"Failed to download", green=False)
            self.initialSize = None
            self.SwitchButtonState(False)
            self.hideProgressBar()

    def showProgressBar(self):
        self.progressbar.pack_configure(after=self.DownloadButton)
        self.progressbar.set(0)

    def updateProgressBar(self, val):
        self.progressbar.set(val)
        self.showStatus(f"Downloading {val}%")

    def hideProgressBar(self):
        self.progressbar.pack_forget()

    def SwitchButtonState(self, disabled: bool):
        if disabled:
            self.DownloadButton.configure(
                require_redraw=True, fg_color="grey", state=customtkinter.DISABLED
            )

        else:
            self.DownloadButton.configure(
                require_redraw=True, fg_color="#1F6AA5", state=customtkinter.NORMAL
            )

    def startDownload(self):
        url = self.URL_Input.get()
        print("Ads")
        if url == "":
            self.showStatus("Failed to download as invalid or empty URL", green=False)
            return

        thread = Thread(target=self.downloadYouTubeVid, args=(url,))
        thread.start()
        self.SwitchButtonState(disabled=True)
        self.showProgressBar()

    def showStatus(self, status, green=True):
        if self.status != None:
            self.status.pack_forget()
            self.status = None
        if green:
            self.status = customtkinter.CTkLabel(
                master=self, text=f"{status}", text_color="green"
            )
        else:
            self.status = customtkinter.CTkLabel(
                master=self, text=f"{status}", text_color="red"
            )

        try:
            self.status.pack_configure(after=self.progressbar)
        except:
            self.status.pack_configure(after=self.DownloadButton)

    def hideStatus(self):
        self.status.pack_forget()

    def initialPack(self):
        self.logo_label.pack_configure()

        self.URL_Input.pack_configure(after=self.logo_label, fill="x", padx=8, pady=8)
        self.DropDown.pack_configure(after=self.URL_Input)
        self.DownloadButton.pack_configure(after=self.DropDown, pady=8)

        self.creditsLabel.pack_configure(anchor="s")


if __name__ == "__main__":
    app = App()
    app.mainloop()
