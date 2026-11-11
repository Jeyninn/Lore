
import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProfileService } from '../../services/profile';
import html2canvas from 'html2canvas';
interface WritingTheme {
  theme: string;
  similarity_score: number;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit {
  private cdr = inject(ChangeDetectorRef);
  private profileService = inject(ProfileService);

  profile: any = null;
  loading = true;
  error = '';

  ngOnInit(): void {
    this.loadProfile();
  }

  formatKey(key: string | number | symbol): string {
    return String(key).replace(/_/g, ' ');
  }

  get writingThemes(): WritingTheme[] {
    return this.profile?.writing_analysis?.themes ?? [];
  }

  get hasWritingAnalysis(): boolean {
    return this.writingThemes.length > 0;
  }

  getThemeName(theme: string): string {
    return theme
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  loadProfile(): void {
    this.profileService.getProfile().subscribe({
      next: (data) => {
        console.log('Profile received:', data);
        this.profile = data;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Profile error:', err);
        this.error = 'Unable to load your profile. Please try again.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

async downloadIdentityCard(): Promise<void> {
  const card = document.getElementById('lore-identity-card');

  if (!card) {
    console.error('Identity card element not found.');
    return;
  }

  try {
    const canvas = await html2canvas(card, {
      scale: 2,
      backgroundColor: '#0B0614',
      useCORS: true,
      logging: false
    });

    const image = canvas.toDataURL('image/png');

    const link = document.createElement('a');
    link.download = 'LORE-exe-identity.png';
    link.href = image;
    link.click();

  } catch (error) {
    console.error('Unable to generate identity card:', error);
  }
}

  // Map backend archetype IDs to character illustrations
  private characterImages: Record<string, string> = {
    lore_keeper: 'assets/characters/lore_keeper.png',
    chaos_architect: 'assets/characters/chaos_architect.png',
    silent_observer: 'assets/characters/silent_observer.png',
    dreamcore_thinker: 'assets/characters/dreamcore_thinker.png',
    digital_nomad: 'assets/characters/digital_nomad.png',
    main_character: 'assets/characters/main_character.png',
    midnight_philosopher: 'assets/characters/midnight_philosopher.png',
    social_butterfly: 'assets/characters/social_butterfly.png',
    creative_glitch: 'assets/characters/creative_glitch.png',
    plot_twister: 'assets/characters/plot_twister.png',
    soft_rebel: 'assets/characters/soft_rebel.png',
    curious_goblin: 'assets/characters/curious_goblin.png'
  };

  get primaryCharacterImage(): string {
    const archetypeId = this.profile?.primary_archetype?.id;

    return this.characterImages[archetypeId]
      ?? 'assets/characters/lore_keeper.png';
  }

  get secondaryCharacterImage(): string {
  const archetypeId = this.profile?.secondary_archetype?.id;

  return this.characterImages[archetypeId]
    ?? 'assets/characters/lore_keeper.png';
}

}
