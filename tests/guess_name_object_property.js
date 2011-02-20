// We should be able to guess both the name and type of this property.
// (a function named "destroy")

    /**
     * Stops the server from accepting new connections. This function is
     * asynchronous, the server is finally closed when the server emits a
     * 'close' event.
     */
    destroy: function() {
        if (this._process) {
            this._process.kill();
            this._process = null;
        }
        this.stdin.destroy();
        this.stdout.destroy();
        this.stderr.destroy();
        this._removeAllListeners("exit")
        delete processes[this._guid];
    }
