// Profile Monitor SlicLet
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { Component } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { APIService } from '../api.service';

@Component({
    selector: 'app-screen',
    template: `
  <div class="row">
    <div *ngIf="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>
    <div class="col-sm-3 ">

      <form>
        <div class="mb-3">
          <label class="form-label">Beam Path</label>
          <select class="form-select form-control-sm">
            <option *ngFor="let bp of beamPaths" [value]="bp">{{ bp }}</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Camera</label>
          <select class="form-select form-control-sm">
            <option *ngFor="let c of cameras" [value]="c">{{ c }}</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">PV</label>
          <input class="form-control form-control-sm" value="OTRS:LI21:291"/>
        </div>

        <div class="mb-3">
          <div class="row">
            <div class="col-sm-4">
              <button [disabled]="isAcquiring" class="btn btn-primary" type="button" (click)="startAcquiringImages()">Start</button>
            </div>
            <div class="col-sm-4">
              <button [disabled]="! isAcquiring" class="btn btn-danger" type="button" (click)="stopAcquiringImages()">Stop</button>
            </div>
            <div class="col-sm-4">
              <button [disabled]="isAcquiring" class="btn btn-outline-dark" type="button" (click)="getSingleImage()">Single</button>
            </div>
          </div>
        </div>
      </form>

    </div>

    <div class="col-sm-9 col-xxl-7">
      <div *ngIf="image && image.raw_pixels.length">
        <app-heatmap-with-lineouts [data]="image"></app-heatmap-with-lineouts>
      </div>
    </div>


    <div class="col-sm-3 "></div>
    <div *ngIf="image && image.raw_pixels.length" style="margin-top: 3ex" class="col-sm-9">

      <form>
        <div class="mb-3">
          <div class="row">
            <div class="col-sm-3">
              <label class="form-label">Curve Fit Method</label>
              <select class="form-select form-control-sm" (change)="selectCurveFit($event)">
                <option *ngFor="let m of methods" [value]="m[0]">{{ m[1] }}</option>
              </select>
            </div>
            <div class="col-sm-3">
              <label class="form-label">Color Map</label>
              <select class="form-select form-control-sm">
                <option *ngFor="let cm of colorMaps" [value]="cm">{{ cm }}</option>
              </select>
            </div>
          </div>
        </div>
      </form>

    </div>
  </div>
    `,
    styles: [],
})
export class ScreenComponent {
    readonly APP_NAME: string = 'screen';
    image: any = null;
    beamPaths: string[] = [];
    cameras = [
        'VCCB',
    ];
    colorMaps: string[] = [];
    methods: any = [];
    errorMessage: string = "";
    isAcquiring: boolean = false;
    interval: any = null;
    curveFit = "gaussian";

    constructor(private apiService: APIService) {
        this.apiService = apiService;

        this.apiService.call('init_app', {
            app_name: this.APP_NAME,
        }).subscribe({
            next: (result) => {
                console.log('init_app result:', result);
                //TODO(pjm): these details move to field editors
                this.beamPaths = result.schema.constants.BeamPath.map((b: any) => b.name);
                this.methods = result.schema.constants.CurveFitMethod;
                this.colorMaps = result.schema.constants.ColorMap;
                this.isAcquiringImages(() => {
                    this.getImages();
                });
            },
            error: (err) => {
                this.handleError(err);
            },
        });
    }

    getImage(callback: Function | null) {
        this.apiService.call('action', {
            app_name: this.APP_NAME,
            method: 'get_image',
            curve_fit: this.curveFit,
        }).subscribe({
            next: (result) => {
                this.image = result;
                if (callback) {
                    callback();
                }
            },
            error: (err) => {
                this.image = null;
                this.handleError(err);
            },
        });
    }

    getImages() {
        let ready = true;
        this.interval = setInterval(() => {
            if (ready) {
                ready = false;
                this.getImage(() => {
                    ready = true;
                });
            }
        }, 1000);
    }

    getSingleImage() {
        if (this.isAcquiring) {
            return;
        }
        this.acquireImages('start_button', () => {
            this.getImage(() => {
                this.stopAcquiringImages();
            });
        });
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

    isAcquiringImages(callback: Function) {
        //TODO(pjm): consolidate calling method w/errorMessage handling
        this.errorMessage = "";
        this.apiService.call('action', {
            app_name: this.APP_NAME,
            method: 'is_acquiring_images',
        }).subscribe({
            next: (result) => {
                this.isAcquiring = result.is_acquiring_images;
                if (result.is_acquiring_images) {
                    callback();
                }
            },
            error: (err) => {
                this.handleError(err);
            },
        });
    }

    selectCurveFit(event: any) {
        this.curveFit = event.target.value;
    }

    startAcquiringImages() {
        this.acquireImages('start_button', () => {
            this.isAcquiring = true;
            this.getImages();
        });
    }

    stopAcquiringImages() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        this.isAcquiring = false;
        this.acquireImages('stop_button', null);
    }

    private acquireImages(button: string, callback: Function | null) {
        this.errorMessage = "";
        this.apiService.call('action', {
            app_name: this.APP_NAME,
            method: button,
        }).subscribe({
            next: (result) => {
                if (callback) {
                    callback();
                }
            },
            error: (err) => {
                this.handleError(err);
            },
        });
    }
}
