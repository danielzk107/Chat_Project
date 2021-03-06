# Chat_Project

Final project for the course Computer Networking. This readme file will not provide a detailed explanation for the project (for now), but will be used to answer all the theoretical questions in the given task.

## File transfer


In this project, there are two forms of fire transfer: Server to Client and Client to Client. the server to client transfer is a direct download using a simple TCP protocol. The client to client transfer sends the file from one client to the server, who then sends it to the other client, using a fast and reliable implementation of the UDP protocol. In this transfer, with every packet is sent a packet number, that must match the current packet number saved on the receiving side. The sender will not proceed to the next packet until they got confirmation that the other side has received the previous one. The receiving side, that is, the server, will only send confirmation for a received packet if it itself has confirmation that the other client has successfully gotten the said packet. That way, we avoid packet loss and latency-related issues while transferring our files.

## Theoretical questions given with the task


1) When a computer joins a new network, it first has to know its own address. In order to get that information, the computer uses its physical layer to send a request for a connection to the new network. To reach the DHCP server, which assigns an address for the computer dynamically, the computer sends its request to the switch connected to it. The switch sends that request in the network and the request is answered by the DHCP server, which sends all the related information (IP address, address of DNS server, etc.) to the computer. The communications between the computer and the server are able to occur because the switch knows the MAC address of the newly connected computer. Since the interaction uses the switch exclusively, the server and computer can communicate. When we want to send a message with our newly connected computer, we first need to find the address of our message's recipient. For that we turn to our DNS server and ask for the address that corresponds to the details we have. We then make a connection using our router, and send our wanted message using a protocol such as TCP\UDP or HTTP\HTTPS, depending on whom we send the message to.


2) CRC is a checksum algorithm, used to detect issues in transferring data. Before sending a packet, the CRC algorithms converts it to binary and divides that number by a known number using binary division. Then, when the packet is sent, the product of the division is sent along with it, for the other side to confirm that no errors were made. When the packet, together with the division product, arrives to the client, the CRC algorithms works again. The information in the packet is again converted to a binary number, and the algorithm adds the previous CRC value to it (in terms of adjacent addition rather than mathematical addition). The result is then divided by a known number (same as the number in the first CRC calculation). If the result has no remainder, then the packet most likely arrived without any data loss. If the result has a remainder, then the data has been corrupted.


3) HTTP 1.0 is an application level protocol used on the World Wide Web to communicate between the client and server to send requests, answers, and data in general. HTTP 1.0 uses TCP as a transport protocol to make all its communications. HTTP1.1 is an improved version of HTTP1.0 that is more efficient, easier to use, and just generally better. As one of its improvements over HTTP1.0, HTTP1.1 can reuse existing TCP connections to connect to other servers, while HTTP1.0 creates a new connection every time. HTTP2.0 is a newer rendition of the protocol, which improves on HTTP1.1 in various ways. For example, HTTP2.0 introduced multiplexing, which allows the user to perform multiple requests at the same time using a single TCP connection. QUIC is a transport protocol designed to replace the TCP protocol, as it improves on it. The main idea of QUIC is making multiplexed connections using UDP to work much faster, similarly to the idea of multiplexing in HTTP 2.0. For that reason, the protocol HTTP 3.0 has started to become almost a standard, as it is a version of HTTP 2.0 using QUIC instead of TCP.


4) While a client can easily make a connection to a server using its IP address, it may not know how to request a specific function that it wants. For that, there are port numbers, that are used to specify the application within the server that the client wants to access.


5) A subnet is an inner-network, a closed network within a larger one. If networks can be thought of as cities, then subnets are neighborhoods, where the subjects all belong to the same close group (also close in terms of distance\time), and they are also inside a larger group. Subnets are used to avoid inefficient routing by communicating directly within the subnet, instead of routing every message and sending it back to the same neighborhood.


6) A MAC address is essential to performing tasks as connecting to a new network (as in question 1, when it is used to send and receive information about its new address) or identifying individual machines on the LAN. Mac addresses are always unique, unlike IP addresses, which means that by using MAC addresses, we will never have any issues identifying machines on any network. 


7) NAT is an acronym of Network Address Translation, which is the process of translating a global IP address to a local IP address (and vice versa). One of the main differences between a router and a switch is that a router has a NAT table used to translate addresses, but a switch has no NAT process, because switches operate at the data link layer while NAT actions are performed on the network layer.


8) The best solution in the long term is slowly switching to IPv6 addresses, as they have trillions of unique addresses. However, in order for the transfer to flow relatively easy around the world, it must be slow, so other short term solutions are required. One of the best short terms solutions is using NAT to translate the IP address and free more addresses for use.
