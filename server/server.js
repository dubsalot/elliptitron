var net = require('net');
var server = net.createServer(function(connection) { 
   console.log('Client Connected');
   
   connection.on('end', function() {
      console.log('client disconnected');
   });
   
   connection.write('Hello World!\r\n');
   connection.pipe(connection);
});

server.listen(8484, function() { 
   console.log('Server running on http://localhost:8484');
});