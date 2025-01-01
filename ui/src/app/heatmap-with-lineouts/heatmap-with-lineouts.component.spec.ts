import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HeatmapWithLineoutsComponent } from './heatmap-with-lineouts.component';

describe('HeatmapWithLineoutsComponent', () => {
  let component: HeatmapWithLineoutsComponent;
  let fixture: ComponentFixture<HeatmapWithLineoutsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [HeatmapWithLineoutsComponent]
    });
    fixture = TestBed.createComponent(HeatmapWithLineoutsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
