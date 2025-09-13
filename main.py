import folium
from geopy.distance import geodesic
import klvdata
import ffmpeg

def extractKLV(videoLocation, outputFile):
    (
        ffmpeg
        .input(videoLocation)
        .output(outputFile, map="0:d:0", codec='copy', f='data')
        .overwrite_output()
        .run(quiet=True)
    )


def readFileData(fileLocation):
    listOfCoordinates = []
    with open(fileLocation, "rb") as file:
        stream = klvdata.StreamParser(file)
        print(stream)
        for index, packet in enumerate(stream):
            print(f"\nPacket {index}")
            metadata = packet.MetadataList()
            coordinates = [0, 0]
            for data in metadata.values():
                print(data)
                if data[0] == "Sensor Latitude":
                    coordinates[0] = float(data[3])
                elif data[0] == "Sensor Longitude":
                    coordinates[1] = float(data[3])
            listOfCoordinates.append(coordinates)
    return listOfCoordinates


def create_map(file, initialCoordinates):
    lat, long = initialCoordinates
    location_map = folium.Map(location=[lat, long], zoom_start=13)
    return location_map


def getMessage(index, listOfCoordinates):
    if index == 0:
        return ("First Point")
    else:
        newCoordinates = listOfCoordinates[index]
        oldCoordinates = listOfCoordinates[index-1]
        distance = geodesic(newCoordinates, oldCoordinates).kilometers #Might change to meters
        return round(distance, 3) #Rounds to 3 digit but can change later if needed


def mark_location_on_map(newCoordinates, mapOject, file, message):
    latitude, longitude = newCoordinates
    marker = folium.Marker(
        [latitude, longitude],
        popup=f"{message}", #Default message
        tooltip="Click for more info"
    )
    marker.add_to(mapOject)
    mapOject.save(file)


def drawLine(listOfCoordinates, mapObject, file):
    mapWithLines = folium.PolyLine(listOfCoordinates,
                                   color="blue",
                                   wight=2.5,
                                   opacity=0.8) #Line colour and stuff can be changed later if I want
    mapWithLines.add_to(mapObject)
    mapObject.save(file)


def markAll(listOfCoordinates, mapObject, file):
    for index, newCoordinates in enumerate(listOfCoordinates):
        message = getMessage(index, listOfCoordinates)
        mark_location_on_map(newCoordinates, mapObject, file, message)


def main():
    videoLocation="Day Flight.mpg"
    outputFile="output.bin"
    extractKLV(videoLocation, outputFile)
    listOfCoordinates = readFileData("output.bin")
    file = "map.html"
    mapObject = create_map(file, listOfCoordinates[0])
    markAll(listOfCoordinates, mapObject, file)
    drawLine(listOfCoordinates, mapObject, file)


if __name__ == "__main__":
    main()