import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfileMonitorComponent } from './profile-monitor.component';

describe('ProfileMonitorComponent', () => {
  let component: ProfileMonitorComponent;
  let fixture: ComponentFixture<ProfileMonitorComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ProfileMonitorComponent]
    });
    fixture = TestBed.createComponent(ProfileMonitorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
