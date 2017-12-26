var express = require('express');
var app = express();
var path = require('path');

var index = path.join(__dirname, 'index.html');
var port = process.argv[2];
var net = path.join(process.cwd(), process.argv[3]);
var pcb = path.join(process.cwd(), process.argv[4]);

app.use('/css', express.static(path.join(__dirname, 'css')));
app.use('/js', express.static(path.join(__dirname, 'js')));

app.get('/', function(req, res) {
    res.sendFile(index);
});

app.get('/net', function(req, res) {
    res.sendFile(net);
});

app.get('/pcb', function(req, res) {
    res.sendFile(pcb);
});

app.listen(port, function () {
    console.log('Viewer listening on port', port);
    console.log('net file:', net);
    console.log('pcb file:', pcb);
});
