// Logging
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

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

export default new LogService();
