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
          <label class="form-label">Curve Fit Method</label>
          <select class="form-select form-control-sm">
            <option *ngFor="let m of methods" [value]="m[0]">{{ m[1] }}</option>
          </select>
        </div>

        <div class="mb-3">
          <button class="btn btn-primary" type="button" (click)="startAcquiringImages()">Start</button>
        </div>
        <div class="mb-3">
          <button class="btn btn-danger" type="button" (click)="stopAcquiringImages()">Stop</button>
        </div>

      </form>

    </div>

    <div class="col-sm-9 col-xxl-7">
      <div *ngIf="heatmapData && heatmapData.length">
        <app-heatmap-with-lineouts [data]="heatmapData"></app-heatmap-with-lineouts>
      </div>
    </div>


    <div class="col-sm-3 "></div>
    <div style="margin-top: 3ex" class="col-sm-9">

      <form>
        <div class="mb-3">
          <div class="row">
            <div class="col-sm-3">
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
    heatmapData: number[][] = [];
    beamPaths: string[] = [];
    cameras = [
        'VCCB',
    ];
    colorMaps: string[] = [];
    methods: any = [];
    errorMessage: string = "";

    constructor(private apiService: APIService) {
        console.log("constructor ScreenComponent");
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
                this.getImage();
            },
            error: this.handleError,
        });
    }

    getImage() {
        this.apiService.call('action', {
            app_name: this.APP_NAME,
            method: 'get_image',
        }).subscribe({
            next: (result) => {
                console.log('get_image result:', result);
                this.heatmapData = result.raw_pixels;
            },
            error: (err) => {
                this.heatmapData = [];
                this.handleError(err);
            },
        });
    }

    handleError(err: any) {
        this.errorMessage = err;
    }

    startAcquiringImages() {
        this.acquireImages(true);
        this.getImage();
    }

    stopAcquiringImages() {
        this.acquireImages(false);
    }

    private acquireImages(isStart: boolean) {
        this.errorMessage = "";
        this.apiService.call('action', {
            app_name: this.APP_NAME,
            method: 'acquire_button',
            is_start: isStart,
        }).subscribe({
            next: (result) => {
                console.log('acquire_button result:', result);
            },
            error: this.handleError,
        });
    }
}
