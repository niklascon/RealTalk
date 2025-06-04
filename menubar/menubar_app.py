import rumps # type: ignore 
import os

script_path = os.path.dirname(__file__)
rt_icon_path = "../assets/icons/Realtalk_transparent.png"
rt_icon = os.path.join(script_path, rt_icon_path)

class MenuBarApp(rumps.App):
    def __init__(self):
        super(MenuBarApp, self).__init__(
            name="RealTalk",
            icon=rt_icon,
            template=True 
        )
    
        self.menu = ["Hello World"]
    
    @rumps.clicked("Hello World")
    def hello(self, _):
            rumps.alert(title="Hello", message="Hello World!")

if __name__ == "__main__":
     MenuBarApp().run()
     