// Profile Monitor SlicLet
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import { APIService } from '../api.service';
import { Component, Input } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { LogService } from '../log.service';
import { SelectComponent, TextComponent, StaticTextComponent, ButtonComponent } from '../app.component';

//TODO(pjm): move editor components out of this module
@Component({
    selector: 'app-buttons',
    template: `
      <div *ngFor="let item of buttons" style="display: inline">
        <app-field-editor [name]="item" [formGroup]="formGroup" [parent]="parent" [ui_ctx]="ui_ctx"></app-field-editor>
      </div>
    `,
})
export class ButtonsComponent {
    @Input() buttons!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;
}

@Component({
    selector: 'app-columns',
    template: `
      <div class="row">
        <div *ngFor="let item of columns" [ngClass]="'col-' + item.layout">
          <div *ngFor="let row of item.rows">
            <app-layout [layout]="row" [formGroup]="formGroup" [parent]="parent" [ui_ctx]="ui_ctx"></app-layout>
          </div>
        </div>
      </div>
    `,
})
export class ColumnsComponent {
    @Input() columns!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;
}

@Component({
    selector: 'app-field-editor',
    template: `
      <div *ngIf="parent.schema[name] == 'select'">
        <app-select [formGroup]="formGroup" [parent]="parent" [field]="name" [ui_ctx]="ui_ctx"></app-select>
      </div>
      <div *ngIf="parent.schema[name] == 'text'">
        <app-text [formGroup]="formGroup" [parent]="parent" [field]="name" [ui_ctx]="ui_ctx"></app-text>
      </div>
      <div *ngIf="parent.schema[name] == 'static'">
        <app-static-text [formGroup]="formGroup" [parent]="parent" [field]="name" [ui_ctx]="ui_ctx"></app-static-text>
      </div>
      <div *ngIf="parent.schema[name] == 'button'">
        <app-button [formGroup]="formGroup" [parent]="parent" [field]="name" [ui_ctx]="ui_ctx"></app-button>
      </div>
      <div *ngIf="parent.schema[name] == 'plot'">
        <div *ngIf="parent.image && parent.image.raw_pixels.length">
          <app-heatmap-with-lineouts [data]="parent.image" [colorMap]="formGroup.value.color_map"></app-heatmap-with-lineouts>
        </div>
      </div>
    `,
})
export class FieldEditorComponent {
    @Input() name!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;
}


@Component({
    selector: 'app-layout',
    template: `
      <div *ngFor="let item of layout | keyvalue">
        <div *ngIf="item.key == 'name'">
          <app-field-editor [name]="item.value" [formGroup]="formGroup" [parent]="parent" [ui_ctx]="ui_ctx"></app-field-editor>
        </div>
        <div *ngIf="item.key == 'buttons'">
          <app-buttons [buttons]="item.value" [formGroup]="formGroup" [parent]="parent" [ui_ctx]="ui_ctx"></app-buttons>
        </div>
        <div *ngIf="item.key == 'columns'">
          <app-columns [columns]="item.value" [formGroup]="formGroup" [parent]="parent" [ui_ctx]="ui_ctx"></app-columns>
        </div>
      </div>
    `,
})
export class LayoutComponent {
    @Input() layout!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;
}

@Component({
    selector: 'app-screen',
    template: `
      <form [formGroup]="form">
        <div class="row" *ngIf="ui_ctx">
          <div *ngIf="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>
          <app-layout [layout]="layout" [formGroup]="form" [parent]="this" [ui_ctx]="ui_ctx"></app-layout>
        </div>
      </form>
    `,
    styles: [],
})
export class ScreenComponent {
    errorMessage: string = "";
    image: any = null;
    imageTimeout: any = null;

    //TODO(pjm): get schema and layout from yaml def
    schema: any = {
        beam_path: 'select',
        camera: 'select',
        pv: 'static',
        camera_gain: 'text',
        start_button: 'button',
        stop_button: 'button',
        single_button: 'button',
        plot: 'plot',
        curve_fit_method: 'select',
        color_map: 'select',
    }
    layout: any = {
        'columns': [
            {
                'layout': 'sm-3',
                'rows': [
                    {'name': 'beam_path'},
                    {'name': 'camera'},
                    {'name': 'pv'},
                    {'name': 'camera_gain'},
                    {'buttons': [
                        'start_button',
                        'stop_button',
                        'single_button'
                    ]}
                ]
            },
            {
                'layout': 'sm-9 xxl-7',
                'rows': [
                    {'name': 'plot'},
                    {'columns': [
                        {
                            'layout': 'sm-3',
                            'rows': [
                                {'name': 'curve_fit_method'}
                            ]
                        },
                        {
                            'layout': 'sm-3',
                            'rows': [
                                {'name': 'color_map'}
                            ]
                        }
                    ]}
                ]
            }
        ]
    };

    //TODO(pjm): individual editors should add their field to the FormGroup
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
                this.checkAutoRefresh(result);
            },
            this.handleError.bind(this),
        );
    }

    checkAutoRefresh(result: any) {
        if (! result.ui_ctx) {
            return;
        }
        //TODO(pjm): until server callbacks are supported - run a timeout on each plot
        if (result.ui_ctx.plot.auto_refresh) {
            if (! this.imageTimeout) {
                this.imageTimeout = setTimeout(() => {
                    this.serverAction('plot', true);
                    this.imageTimeout = null;
                }, 1000);
            }
        }
        else if (this.imageTimeout) {
            clearTimeout(this.imageTimeout);
            this.imageTimeout = null;
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

    serverAction(field: string, value: any) {
        this.errorMessage = '';
        this.ui_ctx[field].enabled = false;
        this.apiService.call(
            `screen_${field}`, {
                field_value: value,
            },
            (result) => {
                this.checkAutoRefresh(result);
                if (result.plot) {
                    this.image = result.plot;
                }
                if (result.ui_ctx && field in result.ui_ctx && 'enabled' in result.ui_ctx[field]) {
                }
                else {
                    this.ui_ctx[field].enabled = true;
                }
                //TODO(pjm): need to only update changed fields
                // for now, do no updates on "plot" field changes to avoid all fields refreshing
                // otherwise changing gain or curve_fit_method acts badly when plots are being streaming
                if (result.ui_ctx && field != 'plot') {
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
}
