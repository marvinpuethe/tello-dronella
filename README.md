# Tello Dronella :rocket:

Tello Dronella is a set of python scripts to fly and manage swarms of the Tello Edu drone.  
:construction: This project is in early stage so feel free to help get it ready.

# How to fly a single drone :arrow_upper_right: 

1. Switch on the drone
1. Connect your computer to the drone-specific wifi
1. Run `python main.py`

## Simple usage :rocket:

Dronella has a simple script called `main.py`. You can use it to parse txt-files with commands or use it with your keyboard input.

The script operates in two flight operation modes _scripted_ and _interactive_  
Interactive mode will started if you give a file as a parameter to the program or a `command.txt` is found in the script path.  
If not it will start in interactive mode and listen to your keayboard inputs.

> Note: The drone communication is started automatically via `command`

### Scripted mode 

In scripted mode Dronella parses a simple text-file. Each line is parsed and sent to the drone. Try this sample code:

```
takeoff
delay 2
land
```

### Interactive mode

If no parameter is given and no `command.txt` is found it will start in interactive mode. The script will listen to your keyboard input.  
You can type any command found in the [Tello SDK 2.0](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)

## Retrieving the state :wrench:

The current state of the drone is automatically retrieved from the Tello State Stream. The retrieved string is parsed to `DroneState`. You can access it in the Tello class.

```python
drone = Tello()
print(drone.state.height)
```

## How it works :bulb:

Create a drone with `drone = Tello()`. The standard address of your drone is `'192.168.10.1'` if it is in station mode pass the ip to the `Tello()` constructor.
This will start a UDP socket to command the drone via port 8889. A UDP socket to retrieve the state of the drone is also established via port 8890.

Now you are able to pass commands to your drone via `drone.send_command(command)`. See the [Tello SDK 2.0](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf) for reference.  
The commands are being sent to the drone and stored into the log which you can access via `drone.log`. If the command is executed the response from the drone is stored into the `logentry`.

When the command has been sent to the drone the script will wait until it was executed successfully or wait until the maximum timeout (`Tello.MAX_TIME_OUT`) has been reached. If the timeout has been reached the script will try to send the _land_ command to the drone.

The drone is constantly being monitored. The state is retrieved via the UDP socket and the response is parsed into the `dronestate`. The entries can be retrieved via `drone.state`. You can access the elements like `drone.state.height`.

## Keep-alive connection :satellite:

Tello drones have the safety feature to land if no command has been received during the last 15 seconds. To avoid accidental landing the script sends the `sn?`command to the drone.

> Note: If you use `sn?` as a command. You will get a fake response with the value of `Tello.tello_sn.

## Logging :page_facing_up:

Dronella logs each command sent to the drone and stats like the duration for the execution. You can get the log via `drone.log()`