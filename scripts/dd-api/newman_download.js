const newman = require('newman');
const fs = require('fs');
const path = require('path');

const [,, collectionFile, environmentFile, outputFile] = process.argv;

newman.run({
    collection: require(path.resolve(collectionFile)),
    environment: require(path.resolve(environmentFile)),
    reporters: 'cli'
}, function (err, summary) {
    if (err) throw err;

    const execution = summary.run.executions[0];
    const responseBody = execution.response.stream;
    const outDir = path.dirname(outputFile);

    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(outputFile, responseBody);
    console.log(`\nArchivo guardado en: ${outputFile} (${(responseBody.length / 1024).toFixed(2)} KB)`);
});
