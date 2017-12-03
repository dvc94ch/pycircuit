var express = require('express');
var app = express();
var path = require('path');

app.use('/css', express.static('css'));
app.use('/js', express.static('js'));
app.use(express.static('files'));

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname + '/index.html'));
});

app.listen(3000, function () {
    console.log('Viewer listening on port 3000!');
});
