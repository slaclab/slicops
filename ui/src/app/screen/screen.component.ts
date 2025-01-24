// Profile Monitor SlicLet
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { APIService } from '../api.service';
import { Component } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { LogService } from '../log.service';

@Component({
    selector: 'app-screen',
    template: `
  <form [formGroup]="form">
  <div class="row" *ngIf="model">
    <div *ngIf="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>
    <div class="col-sm-3 ">

        <div class="mb-3">
          <label class="col-form-label col-form-label-sm">Beam Path</label>
          <select formControlName="beam_path" class="form-select form-select-sm" (change)="selectChanged('beam_path')" >
            <option *ngFor="let bp of model.beam_path.valid_values" [value]="bp">{{ bp }}</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="col-form-label col-form-label-sm">Camera</label>
          <select formControlName="camera" class="form-select form-select-sm" (change)="selectChanged('camera')">
            <option *ngFor="let c of model.camera.valid_values" [value]="c">{{ c }}</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="col-form-label col-form-label-sm">PV</label>
          <input formControlName="pv" class="form-control form-control-sm form-control-plaintext" />
        </div>
        <div class="mb-3">
          <label class="col-form-label col-form-label-sm">Gain</label>
          <input [readonly]="! model.camera_gain.enabled" formControlName="camera_gain" class="form-control form-control-sm" (keydown)="filterEnterKey($event, 'camera_gain')"/>
        </div>

        <div class="mb-3">
          <div class="row">
            <div class="col-sm-4">
              <button [disabled]="! model.start_button.enabled" class="btn btn-primary" type="button" (click)="serverAction('start_button', true)">Start</button>
            </div>
            <div class="col-sm-4">
              <button [disabled]="! model.stop_button.enabled" class="btn btn-danger" type="button" (click)="serverAction('stop_button', true)">Stop</button>
            </div>
            <div class="col-sm-4">
              <button [disabled]="! model.single_button.enabled" class="btn btn-outline-info" type="button" (click)="serverAction('single_button', true)">Single</button>
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
    <div *ngIf="image && image.raw_pixels.length" style="margin-top: 3ex" class="col-sm-9">

        <div class="mb-3">
          <div class="row">
            <div class="col-sm-3">
              <label class="col-form-label col-form-label-sm">Curve Fit Method</label>
              <select formControlName="curve_fit_method" class="form-select form-select-sm" (change)="selectChanged('curve_fit_method')">
                <option *ngFor="let m of model.curve_fit_method.valid_values" [value]="m[0]">{{ m[1] }}</option>
              </select>
            </div>
            <div class="col-sm-3">
              <label class="col-form-label col-form-label-sm">Color Map</label>
              <select formControlName="color_map" class="form-select form-select-sm" (change)="selectChanged('color_map')">
                <option *ngFor="let cm of model.color_map.valid_values" [value]="cm">{{ cm }}</option>
              </select>
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
    readonly APP_NAME: string = 'screen';
    errorMessage: string = "";
    image: any = null;
    imageInterval: any = null;
    form = new FormGroup({
        beam_path: new FormControl(''),
        camera: new FormControl(''),
        pv: new FormControl(''),
        color_map: new FormControl(''),
        curve_fit_method: new FormControl(''),
        camera_gain: new FormControl(''),
    });
    model: any = null;

    constructor(private apiService: APIService, private log: LogService) {
        this.apiService = apiService;

        this.apiService.call(
            'init_app', {
                app_name: this.APP_NAME,
            },
            (result) => {
                this.model = result.model;
                let v:any = {};
                for (let f in result.model) {
                    v[f] = result.model[f].value;
                }
                this.form.patchValue(v);
            },
            this.handleError.bind(this),
        );
    }

    filterEnterKey(event: KeyboardEvent, field: string) {
        if (event.key === 'Enter') {
            this.serverAction(field, (this.form.controls as any)[field].value);
        }
    }

    handleError(err: any) {
        if (this.errorMessage === undefined) {
            this.log.error(['invalid this', this]);
            throw new Error(`Invalid this in handleError: ${this}`);
        }
        this.log.error(['apiService error', err]);
        this.errorMessage = err;
    }

    selectChanged(field: string) {
        this.serverAction(field, (this.form.controls as any)[field].value);
    }

    serverAction(field: string, value: any) {
        this.errorMessage = '';
        this.model[field].enabled = false;
        this.apiService.call(
            'action', {
                app_name: this.APP_NAME,
                method: 'field_changed',
                field: field,
                value: value,
            },
            (result) => {
                if (result.plot) {
                    this.image = result.plot;
                }
                if (result.model && field in result.model && 'enabled' in result.model[field]) {
                }
                else {
                    this.model[field].enabled = true;
                }
                if (result.model) {
                    Object.assign(this.model, result.model);
                    const values: any = {};
                    for (let f in result.model) {
                        if ('value' in result.model[f]) {
                            values[f] = result.model[f].value;
                        }
                    }
                    this.form.patchValue(values);
                }
            },
            (err) => {
                this.handleError(err);
                this.model[field].enabled = true;
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
