import { Component, Input, OnInit, Renderer2 } from '@angular/core';
import { FormGroup } from '@angular/forms';

/**
 * A series of layout components arranged within a bootstrap column class.
 * Attributes are:
 *  - columns: a group of column definitions:
 *    - ngClass: the col-* class
 *    - rows: a group of layout definitions
 */
@Component({
    selector: 'app-columns',
    template: `
      <div class="row">
        <div *ngFor="let col of columns" [ngClass]="'col-' + col.layout">
          <div *ngFor="let row of col.rows">
            <app-layout [layout]="row" [formGroup]="formGroup" [parent]="parent"
              [ui_ctx]="ui_ctx"></app-layout>
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

/**
 * Field editor based on ui_ctx field type.
 */
@Component({
    selector: 'app-field-editor',
    template: `
      <div [ngSwitch]="ui_ctx[name].type">
      <div *ngSwitchCase="'select'">
        <app-select [formGroup]="formGroup" [parent]="parent" [field]="name"
          [ui_ctx]="ui_ctx"></app-select>
      </div>
      <div *ngSwitchCase="'text'">
        <app-text [formGroup]="formGroup" [parent]="parent" [field]="name"
          [ui_ctx]="ui_ctx"></app-text>
      </div>
      <div *ngSwitchCase="'static'">
        <app-static-text [formGroup]="formGroup" [parent]="parent" [field]="name"
          [ui_ctx]="ui_ctx"></app-static-text>
      </div>
      <div *ngSwitchCase="'button'">
        <app-button [formGroup]="formGroup" [parent]="parent" [field]="name"
          [ui_ctx]="ui_ctx"></app-button>
      </div>
      <div *ngSwitchCase="'heatmap_with_lineouts'">
        <div *ngIf="parent.image && parent.image.raw_pixels.length">
          <app-heatmap-with-lineouts [data]="parent.image"
            [colorMap]="formGroup.value.color_map"></app-heatmap-with-lineouts>
        </div>
      </div>
    `,
})
export class FieldEditorComponent implements OnInit{
    @Input() name!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;

    ngOnInit() {
        if (! (this.name in this.ui_ctx)) {
            // display a better console error message when the app is misconfigured
            throw new Error(`Layout field ${this.name} is missing from ui_ctx (${Object.keys(this.ui_ctx)})`);
        }
    }
}

/**
 * Top level page layout. Supports three types:
 *  - name: field editor
 *  - row: a group of field editors arranged in a horizontal row
 *  - columns: a group of columns
 */
@Component({
    selector: 'app-layout',
    template: `
      <div *ngFor="let item of layout | keyvalue">
        <div *ngIf="item.key == 'name'">
          <app-field-editor [name]="item.value" [formGroup]="formGroup" [parent]="parent"
            [ui_ctx]="ui_ctx"></app-field-editor>
        </div>
        <div *ngIf="item.key == 'row'">
          <app-row [row]="item.value" [formGroup]="formGroup" [parent]="parent"
            [ui_ctx]="ui_ctx"></app-row>
        </div>
        <div *ngIf="item.key == 'columns'">
          <app-columns [columns]="item.value" [formGroup]="formGroup" [parent]="parent"
            [ui_ctx]="ui_ctx"></app-columns>
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
    selector: 'app-row',
    template: `
      <div [style]="'column-count:' + row.length">
        <div *ngFor="let item of row" style="display: inline">
          <app-field-editor [name]="item" [formGroup]="formGroup" [parent]="parent"
            [ui_ctx]="ui_ctx"></app-field-editor>
        </div>
      </div>
    `,
})
export class RowComponent {
    @Input() row!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;
}
