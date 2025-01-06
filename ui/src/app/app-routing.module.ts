import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ScreenComponent } from './screen/screen.component';

const routes: Routes = [
    {
        path: '',
        redirectTo: 'screen',
        pathMatch: 'full',
    },
    {
        path: 'screen',
        component: ScreenComponent,
        pathMatch: 'full',
        title: 'Profile Monitor',
    },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
