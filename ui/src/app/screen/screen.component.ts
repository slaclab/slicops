// Profile Monitor SlicLet
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { APIService } from '../api.service';
import { Component } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import { LogService } from '../log.service';

@Component({
    selector: 'app-screen',
    template: `
      <form [formGroup]="form">
        <div class="row" *ngIf="ui_ctx">
          <div *ngIf="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>
          <app-layout [layout]="layout" [formGroup]="form" [parent]="this"
            [ui_ctx]="ui_ctx"></app-layout>
        </div>
      </form>
    `,
    styles: [],
})
export class ScreenComponent {
    errorMessage: string = "";
    image: any = null;
    imageTimeout: any = null;
    layout: any = null;
    form: FormGroup = new FormGroup({});
    ui_ctx: any = null;

    constructor(private apiService: APIService, private log: LogService) {
        this.apiService.call(
            'screen_ui_ctx',
            {},
            (result) => {
                this.ui_ctx = result.ui_ctx;
                this.layout = result.layout;
                let v:any = {};
                for (let f in result.ui_ctx) {
                    v[f] = result.ui_ctx[f].value;
                    this.form.addControl(f, new FormControl(''));
                }
                this.form.patchValue(v);
            },
            this.handleError.bind(this),
        );
        return;
        this.apiService.subscribe(
            'screen_update',
            {},
            (result) => {
                this.ui_ctx = result.ui_ctx;
                this.layout = result.layout;
                let v:any = {};
                for (let f in result.ui_ctx) {
                    v[f] = result.ui_ctx[f].value;
                    this.form.addControl(f, new FormControl(''));
                }
                this.form.patchValue(v);
            },
            this.handleError.bind(this),
        );
    }

    handleError(err: any) {
        if (this.errorMessage === undefined) {
            // This would only happen if the handleError callback is setup incorrectly
            this.log.error(['invalid this', this]);
            throw new Error(`Invalid this in handleError: ${this}`);
        }
        this.log.error(['apiService error', err]);
        this.errorMessage = err;
    }

    serverUpdate(result: any) {
        if (result.plot) {
            this.image = result.plot;
        }
    }

    serverAction(field: string, value: any) {
        this.errorMessage = '';
        this.ui_ctx[field].enabled = false;
        this.apiService.call(
            `screen_${field}`, {
                field_value: value,
            },
            (result) => {
                if (result.ui_ctx && field in result.ui_ctx && 'enabled' in result.ui_ctx[field]) {
                }
                else {
                    this.ui_ctx[field].enabled = true;
                }
                //TODO(pjm): need to only update changed fields
                // for now, do no updates on "plot" field changes to avoid all fields refreshing
                // otherwise changing gain or curve_fit_method acts badly when plots are being streamed
                this.serverUpdate(result);

                Object.assign(this.ui_ctx, result.ui_ctx);
                const values: any = {};
                for (let f in result.ui_ctx) {
                    if ('value' in result.ui_ctx[f]) {
                        values[f] = result.ui_ctx[f].value;
                    }
                }
                this.form.patchValue(values);
            },
            (err) => {
                this.handleError(err);
                this.ui_ctx[field].enabled = true;
            }
        );
    }
}
