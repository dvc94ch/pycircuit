var express = require('express');
var app = express();
var path = require('path');

function random_port() {
    return Math.floor(Math.random() * 100) + 3000;
}

var index = path.join(__dirname, 'index.html');
var port = process.argv[2] || random_port();
var net = path.join(process.cwd(), process.argv[3] || path.join('build', 'net.dot.svg'));
var pcb = path.join(process.cwd(), process.argv[4] || path.join('build', 'pcb.svg'));

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
