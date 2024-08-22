#------------------------------------------------------------------------------
# OIDC configuration script
#  usage:
# wsadmin.sh -f configureOIDC.py nodeName serverName configFile
#
#------------------------------------------------------------------------------
import sys, traceback
import ConfigParser

verbose = False

cell = ""
node = ""
server = ""

#------------------------------------------------------------------------------
# Configure
#------------------------------------------------------------------------------
def doConfigure(nodeName,serverName):
    
    global cell
    global node
    global server
    
    topology = getCellNodeServer()
    if topology == None:
        sys.stderr.write("Could not find suitable server\n")
        if failOnError == "true":
                sys.exit(105)
    else:
        cell = topology[0]
        type = topology[3]
        node = nodeName
        server = serverName
        idString = '/Cell:' + cell + '/Node:' + nodeName + '/Server:' + serverName + '/'
        
        enableHPELLogging()

        AdminConfig.save()
            
        return 1
#endDef


#------------------------------------------------------------------------------
# Add users
#------------------------------------------------------------------------------
def enableHPELLogging():

    print('  +Enable HPEL Logging ...')
    HPELService = AdminConfig.getid('/Cell:'+cell+'/Node:'+node+'/Server:'+server+'/HighPerformanceExtensibleLogging:/')
    AdminConfig.modify(HPELService, "[[enable true]]")
    RASLogging = AdminConfig.getid('/Cell:'+cell+'/Node:'+node+'/Server:'+server+'/RASLoggingService:/')
    AdminConfig.modify(RASLogging, "[[enable false]]")
    print('  -Enable HPEL Logging ...')

#endDef

#------------------------------------------------------------------------------
# Get a tuple containing the cell, node, server name, and type
#------------------------------------------------------------------------------
def getCellNodeServer():
        servers = AdminConfig.list("Server").splitlines()
        for serverId in servers:
                serverName = serverId.split("(")[0]
                server = serverId.split("(")[1]  #remove name( from id
                server = server.split("/")
                cell = server[1]
                node = server[3]
                cellId = AdminConfig.getid("/Cell:" + cell + "/")
                cellType = AdminConfig.showAttribute(cellId, "cellType")
                if cellType == "DISTRIBUTED":
                        if AdminConfig.showAttribute(serverId, "serverType") == "DEPLOYMENT_MANAGER":
                                return (cell, node, serverName, "DEPLOYMENT_MANAGER")
                elif cellType == "STANDALONE":
                        if AdminConfig.showAttribute(serverId, "serverType") == "APPLICATION_SERVER":
                                return (cell, node, serverName, "APPLICATION_SERVER")
        return None
#endDef

#------------------------------------------------------------------------------
# Main entry point
#------------------------------------------------------------------------------

failOnError = "false"

if len(sys.argv) < 1 or len(sys.argv) > 2:
        sys.stderr.write("Invalid number of arguments\n")
        sys.exit(101)
else:
    # Non cluster case
    nodeName = sys.argv[0]
    serverName = sys.argv[1]
    
    print "--------------------------"
    print "Configuring WebSphere"
    print "--------------------------"
    print ""
    print "  Node: " + nodeName
    print "  Server: " + serverName

    doConfigure(nodeName,serverName)
