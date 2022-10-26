# get all Garmin products satisfying a minimum memory requirement.

# 1. copy everything from https://developer.garmin.com/connect-iq/reference-guides/devices-reference/#forerunner%C2%AE745
#   into a text file "garmin-device-reference.txt".
# 2. set `first_device_line` and `last_device_line`.
# 3. run!

def startswith_any(line: str, prefixes: list[str]):
    for prefix in prefixes:
        if line.startswith(prefix):
            return True

    return False

#

def generate_manifest_products(devices: list):
    for device in devices:
        print(f'<iq:product id="{device}" />')

def analyse(filename: str, app_type: str, min_memory: int):
    lines = []
    supported_devices = []
    unsupported_devices = []

    print("reading ...")

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    print("analysing ...", "\n")

    current_device = ""

    for line in lines:
        if line.startswith("Id"):
            current_device = line.split("	")[1].strip()

        elif line.startswith(app_type):
            memory = int(line.split("	")[1].strip())

            if memory >= min_memory:
                supported_devices.append(current_device)
            else:
                unsupported_devices.append(current_device)

    n_supported = len(supported_devices)
    n_unsupported = len(unsupported_devices)
    n_total = n_supported + n_unsupported
    quota = n_supported / n_total

    print(supported_devices, "\n")
    print(f"{n_supported}/{n_total} supported ({int(round(quota, 2) * 100)}%)", "\n")

    return supported_devices

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

def main():
    filename = "garmin-device-reference"
    app_type = "Widget"

    first_device_line = 3
    last_device_line = 110

    memory_745 = 1048576
    memory_245 = 65536

    generate_markdown(f"{filename}.txt", f"{filename}.md", first_device_line, last_device_line)
    #clean("garmin-device-reference.md", "garmin-device-memory.md")

    supported_devices = analyse(f"{filename}.md", app_type, memory_745)
    generate_manifest_products(supported_devices)

if __name__ == "__main__":
    print()
    main()
    print()
