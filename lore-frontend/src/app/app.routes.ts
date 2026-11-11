
import { Routes } from '@angular/router';

import { Home } from './components/home/home';
import { Login } from './components/login/login';
import { Signup } from './components/signup/signup';
import { Profile } from './components/profile/profile';
import { Questionnaire } from './components/questionnaire/questionnaire';
import { Processing } from './components/processing/processing';

import { authGuard } from './guards/auth-guard';
export const routes: Routes = [

  { path: '', redirectTo: 'home', pathMatch: 'full' },

  { path: 'home', component: Home },

  { path: 'login', component: Login },

  { path: 'signup', component: Signup },

  {
    path: 'questionnaire',
    component: Questionnaire,
    canActivate: [authGuard]
  },

  {
    path: 'processing',
    component: Processing,
    canActivate: [authGuard]
  },

  {
    path: 'profile',
    component: Profile,
    canActivate: [authGuard]
  },

  { path: '**', redirectTo: 'home' }

];
