# distributed-file-system
A RESTful distributed NFS implemented in python that implements features such as transparent file access, locking, caching, a directory service, file replication.

## Basic Structure
### Client End
- A client using the file system has six option upon startup, they can read, write, create and delete files, they can also find out which files are stored on the file system by using the 'show' command and find information on the syntax of the commmands using the 'help' command.
- The client does not need any information about what goes on behind these commands, except for the address of the *Registry Server*, this is the server that stores the whereabouts of each other server in the system. This address will be constant throughout the lifetime of the system.
- For example to read a file, the syntax is as as simple as *read <file_name>* and everything else is handled under the hood.

## Servers
### File Server
- The file servers are completely stateless, they have two apis:
- The first allows get for read file, post for write/create file and delete for delete file
- The second is included in every server except the registry server, it is an api that allows get for allowing other servers to check if the server is running and delete for shutting the server down
### Directory Server
- The directory server is at the center of a lot of the functionality of the system and has the following features:
- 5 endpoints
  - The first 
### Registry Server
### Locking Server
### Cache Server (runs locally on the clients machine)



