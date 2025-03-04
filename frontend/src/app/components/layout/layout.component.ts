import { ProfileService } from './../../data/services/profile.service';
import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from '../sidebar/sidebar.component';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss',
})
export class LayoutComponent {
  profileService: ProfileService = inject(ProfileService);

  ngOnInit() {
    this.profileService.getMe().subscribe((val) => {
      console.log(val);
    });
  }
}
