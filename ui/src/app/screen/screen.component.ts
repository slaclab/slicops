// Profile Monitor SlicLet
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { APIService } from '../api.service';
import { Component } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';

@Component({
    selector: 'app-screen',
    template: `
  <form [formGroup]="form">
  <div class="row">
    <div *ngIf="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>
    <div class="col-sm-3 ">

        <div class="mb-3">
          <label class="form-label">Beam Path</label>
          <select formControlName="beam_path" class="form-select form-control-sm">
            <option *ngFor="let bp of beamPaths" [value]="bp">{{ bp }}</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Camera</label>
          <select formControlName="camera" class="form-select form-control-sm">
            <option *ngFor="let c of cameras" [value]="c">{{ c }}</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">PV</label>
          <input formControlName="pv" class="form-control form-control-sm form-control-plaintext" />
        </div>
        <div class="mb-3">
          <label class="form-label">Gain</label>
          <input formControlName="camera_gain" class="form-control form-control-sm" (keydown)="gainKeyDown($event)"/>
        </div>

        <div class="mb-3">
          <div class="row">
            <div class="col-sm-4">
              <button [disabled]="isAcquiring || ! form.value.pv" class="btn btn-primary" type="button" (click)="startAcquiringImages()">Start</button>
            </div>
            <div class="col-sm-4">
              <button [disabled]="! isAcquiring || ! form.value.pv" class="btn btn-danger" type="button" (click)="stopAcquiringImages()">Stop</button>
            </div>
            <div class="col-sm-4">
              <button [disabled]="isAcquiring || ! form.value.pv" class="btn btn-outline-info" type="button" (click)="getSingleImage()">Single</button>
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
              <label class="form-label">Curve Fit Method</label>
              <select formControlName="curve_fit_method" class="form-select form-control-sm">
                <option *ngFor="let m of methods" [value]="m[0]">{{ m[1] }}</option>
              </select>
            </div>
            <div class="col-sm-3">
              <label class="form-label">Color Map</label>
              <select formControlName="color_map" class="form-select form-control-sm">
                <option *ngFor="let cm of colorMaps" [value]="cm">{{ cm }}</option>
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
    beamPathInfo: any = null;
    beamPaths: string[] = [];
    cameras: string[] = [];
    colorMaps: string[] = [];
    errorMessage: string = "";
    image: any = null;
    imageInterval: any = null;
    isAcquiring: boolean = false;
    methods: any = [];

    form = new FormGroup({
        beam_path: new FormControl(''),
        camera: new FormControl(''),
        pv: new FormControl(''),
        color_map: new FormControl(''),
        curve_fit_method: new FormControl(''),
        camera_gain: new FormControl(''),
    });

    constructor(private apiService: APIService) {
        this.apiService = apiService;

        this.form.valueChanges.subscribe(values => {
            this.updateForm(values);
        });

        this.apiService.call('init_app', {
            app_name: this.APP_NAME,
        }).subscribe({
            next: (result) => {
                //TODO(pjm): these details move to field editors
                this.beamPathInfo = result.schema.constants.BeamPath;
                this.beamPaths = Object.keys(result.schema.constants.BeamPath);
                this.methods = result.schema.constants.CurveFitMethod;
                this.colorMaps = result.schema.constants.ColorMap;
                this.isAcquiring = result.model.screen.is_acquiring_images;
                this.form.patchValue(result.model.screen);
                if (this.isAcquiring) {
                    this.getImages();
                }
            },
            error: (err) => this.handleError.bind(this),
        });
    }

    gainKeyDown(event: KeyboardEvent) {
        if (event.key === 'Enter') {
            this.form.controls.camera_gain.disable();
            this.apiService.call('action', {
                app_name: this.APP_NAME,
                method: 'camera_gain',
                camera_gain: this.form.controls.camera_gain.value
            }).subscribe({
                next: (result) => {
                    this.form.controls.camera_gain.enable();
                },
                error: (err) => {
                    this.form.controls.camera_gain.enable();
                    this.handleError(err);
                }
            });

        }
    }

    getSingleImage() {
        if (this.isAcquiring) {
            return;
        }
        this.acquireImages('single_button');
    }

    handleError(err: any) {
        if (this.errorMessage === undefined) {
            throw new Error(`Invalid this in handleError: ${this}`);
        }
        if (err && err.target instanceof WebSocket) {
            err = "WebSocket connection to server failed";
        }
        this.errorMessage = err;
    }

    startAcquiringImages() {
        this.isAcquiring = true;
        this.acquireImages('start_button');
    }

    stopAcquiringImages() {
        if (this.imageInterval) {
            clearInterval(this.imageInterval);
            this.imageInterval = null;
        }
        this.isAcquiring = false;
        this.acquireImages('stop_button');
    }

    private acquireImages(button: string) {
        this.errorMessage = "";
        this.apiService.call('action', {
            app_name: this.APP_NAME,
            method: button,
            curve_fit: this.form.controls.curve_fit_method.value,
        }).subscribe({
            next: (result) => {
                if (result.image) {
                    this.image = result.image;
                    if (button == 'start_button') {
                        this.getImages();
                    }
                }
            },
            error: (err) => this.handleError.bind(this),
        });
    }

    private getImage(callback: Function) {
        this.apiService.call('action', {
            app_name: this.APP_NAME,
            method: 'get_image',
            curve_fit: this.form.controls.curve_fit_method.value,
        }).subscribe({
            next: (result) => {
                this.image = result.image;
                callback();
            },
            error: (err) => {
                this.image = null;
                this.handleError(err);
            },
        });
    }

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

    private updateForm(values: any) {
        // Update list of cameras for the selected beam path
        // and the pv for the selected camera
        if (values.beam_path) {
            const c = this.beamPathInfo[values.beam_path];
            this.cameras = Object.keys(c);
            const pv = values.camera && this.cameras.includes(values.camera)
                ? c[values.camera][0]
                : '';
            if (values.pv !== pv) {
                // note: this will fire an update change, calling updateForm() again
                this.form.patchValue({ pv: pv });
            }
        }
    }
}
