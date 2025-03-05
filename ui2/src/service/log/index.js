class LogService {
    dbg(msg) {
        this.#console(new Error(), msg);
    }

    error(msg) {
        this.#console(new Error(), msg);
    }

    info(msg) {
        this.#console(new Error(), msg);
    }

    #caller(stack) {
        if (! stack) {
            return "";
        }
        const s = stack.split(/\r?\n/);
        const l = s[0] == 'Error' ? s[2] : s[1];
        const m = l.match(/^\s*at\s*(\S+)/);
        return m ? m[1] + '()' : l;
    }

    #console(error, msg) {
        if (msg instanceof Array && msg.length < 10) {
            console.log(
                (new Date().toISOString()).substring(11, 19),
                ...msg,
                this.#caller(error.stack || ""),
            );
        }
        else {
            console.log(
                (new Date().toISOString()).substring(11, 19),
                msg,
                this.#caller(error.stack || ""),
            );
        }
    }
}

export const logService = new LogService();
