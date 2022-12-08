# get all Garmin products satisfying a minimum memory requirement.

# 1. copy everything from https://developer.garmin.com/connect-iq/reference-guides/devices-reference/#forerunner%C2%AE745
#   into a text file "garmin-device-reference.txt".
# 2. set `first_device_line` and `last_device_line`.
# 3. run!

class Device:
    def __init__(self, name):
        self.name = name
        self.id = ""

        self.screen_shape = ""
        self.screen_size = ""
        self.display_colors = -1
        self.touch = ""
        self.buttons = ""
        self.launcher_icon_size = ""

        self.memory_audio = -1
        self.memory_background = -1
        self.memory_datafield = -1
        self.memory_glance = -1
        self.memory_app = -1
        self.memory_watchface = -1
        self.memory_widget = -1

        self.screen_technology = ""
        self.api_level = -1

    def __repr__(self) -> str:
        return self.id

    def is_square_or_circular(self) -> bool:
        width, height = self.screen_size.split(" x ")
        return width == height

#

def startswith_any(line: str, prefixes: list[str]):
    for prefix in prefixes:
        if line.startswith(prefix):
            return True

    return False

def get_str(line: str) -> str:
    splits = line.split("	")
    return splits[1].strip() if len(splits) >= 2 else ""

def get_int(line: str) -> int:
    return int(get_str(line))

#

def clean(filename: str, new_filename: str):
    new_lines = []

    print("reading ...")

    with open(filename, "r") as file:
        lines = file.readlines()

        for line in lines:
            if startswith_any(line, ["#", "Background", "Data Field", "Glance", "Watch App", "Widget"]):
                new_lines.append(line)

    print("writing ...")

    with open(new_filename, "w") as file:
        file.writelines(new_lines)

    print("done!")

def generate_markdown(filename: str, new_filename: str, first_device_line: int, last_device_line: int):
    device_lines = []
    text = ""

    print("reading ...")

    with open(filename, "r", encoding="utf-8") as file:
        device_lines = file.readlines()[first_device_line - 1:last_device_line]

    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()

    for line in device_lines:
        name = line.split(" 	")[0]
        text = text.replace(f"\n{name}", f"\n## {name}")

    print("writing ...")

    with open(new_filename, "w", encoding="utf-8") as file:
        file.write(text)

    print("done!")

#

def get_devices(device_reference_filename: str, api_level_filename: str) -> list[Device]:
    device_reference_lines = []
    api_level_lines = []

    print("reading ...")

    with open(device_reference_filename, "r", encoding="utf-8") as file:
        device_reference_lines = file.readlines()

    with open(api_level_filename, "r", encoding="utf-8") as file:
        api_level_lines = file.readlines()

    print("analysing ...", "\n")

    devices = []
    current_device = None

    # read device reference
    for line in device_reference_lines:
        if line.startswith("## "):
            current_device = Device(line[3:])
            devices.append(current_device)
            continue

        if current_device == None:
            continue

        if line.startswith("Id"):
            current_device.id = get_str(line)

        if line.startswith("Screen Shape"):
            current_device.screen_shape = get_str(line)

        if line.startswith("Screen Size"):
            current_device.screen_size = get_str(line)

        if line.startswith("Display Colors"):
            current_device.display_colors = get_int(line)

        if line.startswith("Touch"):
            current_device.touch = get_str(line)

        if line.startswith("Buttons"):
            current_device.buttons = get_str(line)

        if line.startswith("Launcher Icon Size"):
            current_device.launcher_icon_size = get_str(line)

        if line.startswith("Audio Content Provider"):
            current_device.memory_audio = get_int(line)

        if line.startswith("Background"):
            current_device.memory_background = get_int(line)

        if line.startswith("Data Field"):
            current_device.memory_datafield = get_int(line)

        if line.startswith("Glance"):
            current_device.memory_glance = get_int(line)

        if line.startswith("Watch App"):
            current_device.memory_app = get_int(line)

        if line.startswith("Watch Face"):
            current_device.memory_watchface = get_int(line)

        if line.startswith("Widget"):
            current_device.memory_widget = get_int(line)

    # read api level
    for device in devices:
        for i in range(len(api_level_lines) - 1):
            if device.name in api_level_lines[i]:
                _, _, _, screen_technology, api_level = (
                    api_level_lines[i + 1].split("\n")[0].split("	"))

                device.screen_technology = screen_technology
                device.api_level = int(api_level.replace(".", ""))

    return devices

def analyse_supported_devices(devices: list[Device]):
    print("- id: " + str([device.id for device in devices]))
    print()

    print("- screen_shape: " + str(set([device.screen_shape for device in devices])))
    print("- screen_size: " + str(set([device.screen_size for device in devices])))
    print("- display_colors: " + str(set([device.display_colors for device in devices])))
    print("- touch: " + str(set([device.touch for device in devices])))
    print("- buttons: " + str(set([device.buttons for device in devices])))
    print("- launcher_icon_size: " + str(set([device.launcher_icon_size for device in devices])))
    print()

    print("- memory_audio: " + str(set([device.memory_audio for device in devices])))
    print("- memory_background: " + str(set([device.memory_background for device in devices])))
    print("- memory_datafield: " + str(set([device.memory_datafield for device in devices])))
    print("- memory_glance: " + str(set([device.memory_glance for device in devices])))
    print("- memory_app: " + str(set([device.memory_app for device in devices])))
    print("- memory_watchface: " + str(set([device.memory_watchface for device in devices])))
    print("- memory_widget: " + str(set([device.memory_widget for device in devices])))
    print()

    print("- screen_technology: " + str(set([device.screen_technology for device in devices])))
    print("- api_level: " + str(set([device.api_level for device in devices])))
    print()

def print_stats(devices, supported_devices):
    n_supported = len(supported_devices)
    n_total = len(devices)
    quota = n_supported / n_total
    print(f"{n_supported}/{n_total} supported ({int(round(quota, 2) * 100)}%)", "\n")

def generate_manifest_products(devices: list):
    for device in devices:
        print(f'<iq:product id="{device}" />')

#

def main():
    ref_filename = "data/garmin-device-reference"
    api_filename = "data/garmin-device-api-level.txt"

    first_device_line = 3
    last_device_line = 110

    #generate_markdown(f"{filename}.txt", f"{filename}.md", first_device_line, last_device_line)
    #clean("garmin-device-reference.md", "garmin-device-memory.md")

    # memory_widget: {65_536, 262_144, 524_288, 786_432, 1_048_576}
    memory_745 = 1_048_576
    memory_245 = 65_536

    # minimum requirements
    memory_min = 262_144
    api_min = 310

    devices = get_devices(f"{ref_filename}.md", api_filename)

    supported_devices = [device for device in devices
        if device.memory_widget >= memory_min
            and device.api_level >= api_min
            and device.is_square_or_circular()]

    analyse_supported_devices(supported_devices)
    print_stats(devices, supported_devices)
    generate_manifest_products([device.id for device in supported_devices])

if __name__ == "__main__":
    print()
    main()
    print()
