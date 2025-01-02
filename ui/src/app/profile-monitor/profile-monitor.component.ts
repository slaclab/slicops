import { Component } from '@angular/core';
import { AppDataService } from '../app-data.service';
import { FormGroup, FormControl, Validators } from '@angular/forms';

@Component({
    selector: 'app-profile-monitor',
    template: `
<div class="container-fluid">
  <div class="row">
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
        <div class="form-check">
          <input id="statsCheckbox" class="form-check-input" type="checkbox" value="" checked (click)="toggleStats()"/>
          <label class="form-check-label" for="statsCheckbox">
            Calculate Statistics
          </label>
        </div>
        <div class="mb-3" *ngIf="showStats">
          <label class="form-label">Curve Fit Method</label>
          <select class="form-select form-control-sm">
            <option *ngFor="let m of methods" [value]="m">{{ m }}</option>
          </select>
        </div>
        <div class="mb-3"  *ngIf="showStats">
          <div class="col">
            <div class="row">
              <div class="col-sm-2">
                <label class="form-label">xSig</label>
              </div>
              <div class="col-sm-4">
            <input class="form-control form-control-sm text-end" value="4.6" />
              </div>
              <div class="col-sm-2">
            <label class="form-label">ySig</label>
              </div>
              <div class="col-sm-4">
            <input class="form-control form-control-sm text-end" value="4.6" />
              </div>
            </div>
          </div>
        </div>
      </form>

    </div>

    <div class="col-sm-9 col-xxl-7">
      <app-heatmap-with-lineouts *ngIf="showLineouts" [data]="heatmapData"></app-heatmap-with-lineouts>
      <app-heatmap *ngIf="! showLineouts" [data]="heatmapData"></app-heatmap>
    </div>


    <div class="col-sm-3 "></div>
    <div style="margin-top: 3ex" class="col-sm-9">

      <form>
        <div class="mb-3">
          <div class="row">
            <div class="col-sm-3">
              <div class="form-check">
                <input id="lineoutCheckbox" class="form-check-input" type="checkbox" value="" checked (click)=toggleLineouts()/>
                <label class="form-check-label" for="lineoutCheckbox">
                  Show Lineouts
                </label>
              </div>
            </div>
            <div class="col-sm-3">
              <div class="form-check">
                <input id="colorbarCheckbox" class="form-check-input" type="checkbox" value="" />
                <label class="form-check-label" for="colorbarCheckbox">
                  Show Colorbar
                </label>
              </div>
            </div>
            <div class="col-sm-3">
              <select class="form-select form-control-sm">
                <option *ngFor="let cm of colormaps" [value]="cm">{{ cm }}</option>
              </select>
            </div>
            <div class="col-sm-3">
              <select class="form-select form-control-sm">
                <option *ngFor="let bd of bitdepth" [value]="bd">{{ bd }}</option>
              </select>
            </div>
          </div>
        </div>
      </form>

    </div>

  </div>
</div>
    `,
    styles: [],
})
export class ProfileMonitorComponent {
    heatmapData: number[][];
    form = new FormGroup({
        beamPath: new FormControl(''),
        camera: new FormControl(''),
        cameraPV: new FormControl('OTRS:LI21:291'),
        calcStats: new FormControl(''),
        curveMethod: new FormControl(''),
        xSig: new FormControl(''),
        ySig: new FormControl(''),
    });
    showLineouts = true;
    showStats = true;
    beamPaths = [
        'CU_HXR',
        'CU_SXR',
        'SC_DIAG0',
        'SC_BSYD',
        'SC_HXR',
        'SC_SXR',
    ];
    cameras = [
        'VCCB',
    ];
    colormaps = [
        'Inferno',
        'Viridis',
    ];
    methods = [
        'Gaussian',
        'Assymetric',
        'RMS raw',
        'RMS cut peak',
        'RMS cut area',
        'RMS floor',
    ];
    bitdepth = [
        8, 9, 10, 11, 12, 13, 14, 15, 16,
    ];

    constructor(dataService: AppDataService) {
        this.heatmapData = dataService.heatmapData;
    }

    toggleLineouts() {
        this.showLineouts = ! this.showLineouts;
    }

    toggleStats() {
        this.showStats = ! this.showStats;
    }
}
