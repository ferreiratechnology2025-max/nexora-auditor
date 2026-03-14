import { Star, Quote } from 'lucide-react';

interface TestimonialCardProps {
  name: string;
  company: string;
  role: string;
  avatar: string;
  avatarImage?: string;
  rating: number;
  testimonial: string;
  highlight?: string;
}

/**
 * TestimonialCard Component
 * Design: Minimalismo Cirúrgico
 * - Avatar circular com iniciais
 * - Rating em estrelas
 * - Citação destacada
 * - Informações de empresa e cargo
 */
export default function TestimonialCard({
  name,
  company,
  role,
  avatar,
  avatarImage,
  rating,
  testimonial,
  highlight
}: TestimonialCardProps) {
  return (
    <div className="bg-white border border-border rounded-lg p-8 hover:shadow-lg transition-shadow duration-300 flex flex-col h-full">
      {/* Quote Icon */}
      <Quote className="w-6 h-6 text-primary/20 mb-4" />

      {/* Testimonial Text */}
      <p className="text-foreground mb-6 flex-grow">
        {highlight ? (
          <>
            {testimonial.split(highlight)[0]}
            <span className="font-semibold text-primary">{highlight}</span>
            {testimonial.split(highlight)[1]}
          </>
        ) : (
          testimonial
        )}
      </p>

      {/* Rating */}
      <div className="flex gap-1 mb-6">
        {Array.from({ length: 5 }).map((_, i) => (
          <Star
            key={i}
            className={`w-4 h-4 ${
              i < rating ? 'fill-primary text-primary' : 'text-border'
            }`}
          />
        ))}
      </div>

      {/* Author Info */}
      <div className="flex items-center gap-4 pt-6 border-t border-border">
        {/* Avatar */}
        {avatarImage ? (
          <img
            src={avatarImage}
            alt={`${name} - ${role} na ${company}`}
            className="w-12 h-12 rounded-full object-cover border border-border flex-shrink-0"
            width="96"
            height="96"
            loading="lazy"
          />
        ) : (
          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-sm font-bold text-primary">
              {avatar}
            </span>
          </div>
        )}

        {/* Name and Company */}
        <div>
          <p className="font-semibold text-foreground text-sm">{name}</p>
          <p className="text-xs text-muted-foreground">{role}</p>
          <p className="text-xs text-muted-foreground font-medium">{company}</p>
        </div>
      </div>
    </div>
  );
}
