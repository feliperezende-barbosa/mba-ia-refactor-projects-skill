const write = (level, args) => {
    const line = `${new Date().toISOString()} [${level}]`;
    (level === 'ERROR' ? console.error : console.log)(line, ...args);
};

module.exports = {
    info: (...args) => write('INFO', args),
    warn: (...args) => write('WARN', args),
    error: (...args) => write('ERROR', args),
};
