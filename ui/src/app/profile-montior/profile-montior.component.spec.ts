import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfileMontiorComponent } from './profile-montior.component';

describe('ProfileMontiorComponent', () => {
  let component: ProfileMontiorComponent;
  let fixture: ComponentFixture<ProfileMontiorComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ProfileMontiorComponent]
    });
    fixture = TestBed.createComponent(ProfileMontiorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
