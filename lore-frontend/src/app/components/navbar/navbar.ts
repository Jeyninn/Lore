
import { Component ,inject} from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar {
private router = inject(Router);
  get isLoggedIn(): boolean {
    return typeof localStorage !== 'undefined' &&
      !!localStorage.getItem('token');
  }

  logout(): void {
  localStorage.removeItem('token');
  this.router.navigate(['/home']);
}
}
