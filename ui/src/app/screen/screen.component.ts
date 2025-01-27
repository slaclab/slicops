// Profile Monitor SlicLet
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { APIService } from '../api.service';
import { Component } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { LogService } from '../log.service';
import { SelectComponent, TextComponent, StaticTextComponent, ButtonComponent } from '../app.component';

@Component({
    selector: 'app-screen',
    template: `
      <form [formGroup]="form">
        <div class="row" *ngIf="ui_ctx">
          <div *ngIf="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>
          <div class="col-sm-3 ">
            <div class="mb-3">
              <app-select [formGroup]="form" [parent]="this" field="beam_path" [ui_ctx]="ui_ctx"></app-select>
            </div>
            <div class="mb-3">
              <app-select [formGroup]="form" [parent]="this" field="camera" [ui_ctx]="ui_ctx"></app-select>
            </div>
            <div class="mb-3">
              <app-static-text [formGroup]="form" [parent]="this" field="pv" [ui_ctx]="ui_ctx"></app-static-text>
            </div>
            <div class="mb-3">
              <app-text [formGroup]="form" [parent]="this" field="camera_gain" [ui_ctx]="ui_ctx"></app-text>
            </div>
            <div class="mb-3">
              <div class="row">
                <div class="col-sm-4">
                  <app-button [formGroup]="form" [parent]="this" field="start_button" [ui_ctx]="ui_ctx"></app-button>
                </div>
                <div class="col-sm-4">
                  <app-button [formGroup]="form" [parent]="this" field="stop_button" [ui_ctx]="ui_ctx"></app-button>
                </div>
                <div class="col-sm-4">
                  <app-button [formGroup]="form" [parent]="this" field="single_button" [ui_ctx]="ui_ctx"></app-button>
                </div>
              </div>
            </div>
          </div>
          <div class="col-sm-9 col-xxl-7">
            <div *ngIf="image && image.raw_pixels.length">
              <app-heatmap-with-lineouts [data]="image" [colorMap]="form.value.color_map"></app-heatmap-with-lineouts>
            </div>
          </div>
          <div class="col-sm-3 "></div>
          <div *ngIf="image && image.raw_pixels.length" class="col-sm-9">
            <div class="mb-3">
              <div class="row">
                <div class="col-sm-3">
                  <app-select [formGroup]="form" [parent]="this" field="curve_fit_method" [ui_ctx]="ui_ctx"></app-select>
                </div>
                <div class="col-sm-3">
                  <app-select [formGroup]="form" [parent]="this" field="color_map" [ui_ctx]="ui_ctx"></app-select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    `,
    styles: [],
})
export class ScreenComponent {
    errorMessage: string = "";
    image: any = null;
    imageInterval: any = null;

    //TODO(pjm): build form and ui components dynamically from schema view layout
    form = new FormGroup({
        beam_path: new FormControl(''),
        camera: new FormControl(''),
        pv: new FormControl(''),
        color_map: new FormControl(''),
        curve_fit_method: new FormControl(''),
        camera_gain: new FormControl('', [
            Validators.required,
            Validators.pattern("^-?[0-9]+$"),
        ]),
    });
    ui_ctx: any = null;

    constructor(private apiService: APIService, private log: LogService) {
        this.apiService = apiService;

        this.apiService.call(
            'screen_ui_ctx',
            {},
            (result) => {
                this.ui_ctx = result.ui_ctx;
                let v:any = {};
                for (let f in result.ui_ctx) {
                    v[f] = result.ui_ctx[f].value;
                }
                this.form.patchValue(v);
            },
            this.handleError.bind(this),
        );
    }

    handleError(err: any) {
        if (this.errorMessage === undefined) {
            this.log.error(['invalid this', this]);
            throw new Error(`Invalid this in handleError: ${this}`);
        }
        this.log.error(['apiService error', err]);
        this.errorMessage = err;
    }

    serverAction(field: string, value: any) {
        this.errorMessage = '';
        this.ui_ctx[field].enabled = false;
        this.apiService.call(
            `screen_${field}`, {
                field_value: value,
            },
            (result) => {
                if (result.plot) {
                    this.image = result.plot;
                }
                if (result.ui_ctx && field in result.ui_ctx && 'enabled' in result.ui_ctx[field]) {
                }
                else {
                    this.ui_ctx[field].enabled = true;
                }
                if (result.ui_ctx) {
                    Object.assign(this.ui_ctx, result.ui_ctx);
                    const values: any = {};
                    for (let f in result.ui_ctx) {
                        if ('value' in result.ui_ctx[f]) {
                            values[f] = result.ui_ctx[f].value;
                        }
                    }
                    this.form.patchValue(values);
                }
            },
            (err) => {
                this.handleError(err);
                this.ui_ctx[field].enabled = true;
            }
        );
    }

    //TODO(pjm): add poll time to serverAction response to refresh image for now
    /*
    private getImages() {
        let ready = true;
        this.imageInterval = setInterval(() => {
            if (ready) {
                ready = false;
                this.getImage(() => {
                    ready = true;
                });
            }
        }, 1000);
    }
    */
}
