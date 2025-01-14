// Logging
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { Injectable } from '@angular/core';
@Injectable()

export class LogService {
    dbg(msg: any) {
        _console(new Error(), msg);
    }

    warn(msg: any) {
        _console(new Error(), msg);
    }

    _caller(stack: string) {
        if (! stack) {
            return "";
        }
        const l = stack.split(/\r?\n/);
        if (l[0] == 'Error') {
            return l[1];
        }
        return l[0];
    }

    _console(error: Error, msg: any) : string {
        (new Date().toISOString()).substring(11, 19),
        msg,
        _caller(error.stack),
    }
}
